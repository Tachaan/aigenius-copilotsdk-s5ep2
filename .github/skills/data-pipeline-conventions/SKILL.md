---
name: data-pipeline-conventions
description: "Enforces data pipeline coding conventions for retail analytics. Use this skill when writing or reviewing ETL code, data ingestion, transformation logic, or data quality checks. Covers schema management, idempotency, validation, partitioning, and observability patterns for production data pipelines."
license: MIT
---

# Data Pipeline Conventions

Enforce consistent, production-grade patterns for data pipelines in retail analytics systems.

## When to Use

- Writing new ETL or data ingestion code
- Reviewing data transformation logic
- Adding data quality checks or validation
- Designing schema migrations or evolution
- Building batch or streaming data processors
- When asked: "review this pipeline", "check data conventions", "is this ETL correct?"

## Pipeline Architecture Principles

### 1. Idempotency

Every pipeline step MUST be idempotent — re-running with the same input produces the same output without side effects.

```csharp
// ✅ Good: Upsert pattern — safe to re-run
await db.Transactions
    .Where(t => t.CustomerId == customerId && t.Timestamp == timestamp)
    .ExecuteDeleteAsync();
db.Transactions.Add(newTransaction);
await db.SaveChangesAsync();

// ❌ Bad: Insert-only — duplicates on re-run
db.Transactions.Add(newTransaction);
await db.SaveChangesAsync();
```

### 2. Schema Management

| Rule | Convention |
|------|-----------|
| Schema changes | Use EF Core migrations with descriptive names |
| Column additions | Always provide defaults for non-nullable columns |
| Column removals | Two-phase: deprecate → migrate → remove |
| Type changes | Never change column types in-place — add new column, migrate, drop old |
| Naming | Use `snake_case` for database columns, `PascalCase` for C# properties |

### 3. Data Validation

Validate at every boundary — ingestion, transformation, and output.

```csharp
// ✅ Good: Validate before processing
public async Task<Result<Transaction>> IngestTransactionAsync(TransactionInput input)
{
    if (string.IsNullOrWhiteSpace(input.CustomerId))
        return Result.Fail<Transaction>("CustomerId is required");

    if (input.Amount <= 0)
        return Result.Fail<Transaction>("Amount must be positive");

    if (input.Timestamp > DateTime.UtcNow.AddMinutes(5))
        return Result.Fail<Transaction>("Timestamp cannot be in the future");

    if (!ValidCategories.Contains(input.ProductCategory))
        return Result.Fail<Transaction>($"Unknown category: {input.ProductCategory}");

    // Process valid data...
}
```

**Required validation checks:**

| Field Type | Checks |
|------------|--------|
| IDs | Non-empty, valid format, exists in reference data |
| Amounts | Positive, within expected range, correct precision |
| Timestamps | Not in future, within expected window, UTC normalized |
| Categories | Belongs to known set, case-normalized |
| Strings | Trimmed, length limits, no control characters |

### 4. Error Handling & Dead Letter Queues

```csharp
// ✅ Good: Capture failures without blocking the pipeline
public async Task ProcessBatchAsync(IEnumerable<TransactionInput> batch)
{
    var failures = new List<(TransactionInput Input, string Error)>();

    foreach (var input in batch)
    {
        try
        {
            var result = await IngestTransactionAsync(input);
            if (!result.IsSuccess)
                failures.Add((input, result.Error));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process transaction {CustomerId}",
                input.CustomerId);
            failures.Add((input, ex.Message));
        }
    }

    if (failures.Count > 0)
    {
        await WriteToDeadLetterAsync(failures);
        _logger.LogWarning("Batch completed with {FailCount}/{Total} failures",
            failures.Count, batch.Count());
    }
}
```

### 5. Partitioning & Batching

| Pattern | When to Use |
|---------|------------|
| Time partitioning | Transaction data — partition by day/week |
| Key partitioning | Customer data — partition by customer segment |
| Batch size | 1,000–10,000 records per batch for bulk operations |
| Parallel batches | Use `Parallel.ForEachAsync` with bounded concurrency |

```csharp
// ✅ Good: Bounded parallel processing
await Parallel.ForEachAsync(
    batches,
    new ParallelOptions { MaxDegreeOfParallelism = 4 },
    async (batch, ct) => await ProcessBatchAsync(batch, ct));
```

### 6. Observability & Logging

Every pipeline MUST emit structured logs at these points:

| Event | Log Level | Required Fields |
|-------|-----------|-----------------|
| Pipeline start | Information | `pipeline_name`, `batch_id`, `record_count` |
| Validation failure | Warning | `pipeline_name`, `field`, `value`, `reason` |
| Processing error | Error | `pipeline_name`, `record_id`, `exception` |
| Pipeline complete | Information | `pipeline_name`, `batch_id`, `processed`, `failed`, `duration_ms` |
| Data quality alert | Warning | `pipeline_name`, `metric`, `threshold`, `actual` |

```csharp
_logger.LogInformation(
    "Pipeline {Pipeline} completed: {Processed}/{Total} records in {Duration}ms",
    pipelineName, processed, total, stopwatch.ElapsedMilliseconds);
```

### 7. Data Quality Checks

Run automated quality checks after each pipeline stage:

```csharp
public record DataQualityResult(string Check, bool Passed, string Detail);

public async Task<List<DataQualityResult>> RunQualityChecksAsync()
{
    var results = new List<DataQualityResult>();

    // Completeness: no null required fields
    var nullCount = await _db.Transactions.CountAsync(t => t.CustomerId == "");
    results.Add(new("completeness_customer_id",
        nullCount == 0,
        $"{nullCount} records with empty CustomerId"));

    // Freshness: data arrived within expected window
    var latest = await _db.Transactions.MaxAsync(t => t.Timestamp);
    var stale = DateTime.UtcNow - latest > TimeSpan.FromHours(24);
    results.Add(new("freshness_24h",
        !stale,
        $"Latest record: {latest:u}"));

    // Validity: amounts within expected range
    var outliers = await _db.Transactions
        .CountAsync(t => t.Amount < 0 || t.Amount > 100000);
    results.Add(new("validity_amount_range",
        outliers == 0,
        $"{outliers} records outside expected amount range"));

    return results;
}
```

### 8. Naming Conventions

| Artifact | Convention | Example |
|----------|-----------|---------|
| Pipeline class | `{Source}To{Destination}Pipeline` | `PosToWarehousePipeline` |
| Transform method | `Transform{Entity}Async` | `TransformTransactionAsync` |
| Validation method | `Validate{Entity}` | `ValidateTransaction` |
| Quality check | `Check{Metric}` | `CheckCompleteness` |
| Batch ID | `{pipeline}_{yyyyMMdd}_{HHmmss}_{guid:N:8}` | `pos_ingest_20260217_103000_a1b2c3d4` |
| Dead letter table | `{entity}_dead_letter` | `transaction_dead_letter` |

### 9. Testing Data Pipelines

| Test Type | What to Test | Pattern |
|-----------|-------------|---------|
| Unit | Individual transforms | Mock input → assert output |
| Boundary | Edge cases (nulls, empties, max values) | Parameterized tests with `[Theory]` |
| Idempotency | Run twice → same result | Process batch → re-process → assert no duplicates |
| Quality | Quality checks catch known bad data | Inject bad records → assert checks fail |
| Integration | End-to-end pipeline with in-memory DB | Seed → run pipeline → assert output state |

## Review Checklist

When reviewing data pipeline code, verify:

- [ ] Pipeline steps are idempotent
- [ ] All inputs validated at ingestion boundary
- [ ] Errors captured to dead letter, not swallowed
- [ ] Structured logging at start, end, and on failures
- [ ] Batch sizes bounded (not unbounded `ToListAsync()` on full tables)
- [ ] Timestamps normalized to UTC
- [ ] Data quality checks exist for completeness, freshness, and validity
- [ ] Schema changes use migrations, not manual DDL
- [ ] Tests cover happy path, edge cases, and idempotency
- [ ] `CancellationToken` passed through all async methods
