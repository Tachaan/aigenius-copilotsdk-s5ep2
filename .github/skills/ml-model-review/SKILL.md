---
name: ml-model-review
description: "Reviews ML model code for correctness, fairness, and production readiness. Use this skill when writing or reviewing customer segmentation, prediction models, feature engineering, or model evaluation code. Checks for data leakage, bias, reproducibility, and deployment risks in retail analytics ML pipelines."
license: MIT
---

# ML Model Review

Review machine learning model code for correctness, fairness, reproducibility, and production readiness — with a focus on retail analytics patterns like customer segmentation and spend prediction.

## When to Use

- Writing or reviewing customer segmentation logic
- Building or evaluating prediction models (churn, spend, segment classification)
- Reviewing feature engineering code
- Assessing model fairness or bias risk
- Preparing models for production deployment
- When asked: "review this model", "check for data leakage", "is this ML code production-ready?"

## Critical Issues to Detect

### 1. Data Leakage

Data leakage is the #1 cause of models that work in development but fail in production.

**Types to check:**

| Leakage Type | What to Look For | Example |
|-------------|------------------|---------|
| Target leakage | Features derived from the target variable | Using `is_high_value` to predict `segment` |
| Temporal leakage | Future data used to predict past events | Using tomorrow's transactions to predict today's segment |
| Train-test leakage | Test data influencing training (e.g., shared normalization) | Fitting scaler on full dataset before splitting |
| Group leakage | Same customer appearing in train and test sets | Random split without grouping by `CustomerId` |

```csharp
// ❌ Bad: Group leakage — same customer in train and test
var shuffled = transactions.OrderBy(_ => Random.Shared.Next()).ToList();
var train = shuffled.Take(shuffled.Count * 80 / 100).ToList();
var test = shuffled.Skip(shuffled.Count * 80 / 100).ToList();

// ✅ Good: Group-aware split — customers don't cross sets
var customerIds = transactions.Select(t => t.CustomerId).Distinct().ToList();
var trainCustomers = customerIds.Take(customerIds.Count * 80 / 100).ToHashSet();
var train = transactions.Where(t => trainCustomers.Contains(t.CustomerId)).ToList();
var test = transactions.Where(t => !trainCustomers.Contains(t.CustomerId)).ToList();
```

```csharp
// ❌ Bad: Temporal leakage — using future data
var allTransactions = await _db.Transactions
    .Where(t => t.CustomerId == customerId)
    .ToListAsync();
var totalSpend = allTransactions.Sum(t => t.Amount); // includes future!

// ✅ Good: Temporal cutoff — only use data available at prediction time
var asOfDate = predictionDate;
var historicalTransactions = await _db.Transactions
    .Where(t => t.CustomerId == customerId && t.Timestamp < asOfDate)
    .ToListAsync();
var totalSpend = historicalTransactions.Sum(t => t.Amount);
```

### 2. Feature Engineering

| Rule | Convention |
|------|-----------|
| Feature naming | Descriptive: `avg_monthly_spend`, not `f1` or `feature_3` |
| Null handling | Explicit strategy per feature (impute, flag, or exclude) |
| Encoding | Use one-hot for low cardinality, target encoding for high cardinality |
| Scaling | Fit on training data only, apply to test/production |
| Feature documentation | Each feature must have a docstring explaining business meaning |

```csharp
// ✅ Good: Well-documented feature extraction
/// <summary>
/// Extracts ML features for customer segmentation.
/// All features use only historical data up to the cutoff date.
/// </summary>
public record CustomerFeatures(
    /// <summary>Total spend across all categories in the observation window</summary>
    decimal TotalSpend,
    /// <summary>Average transaction amount (TotalSpend / TransactionCount)</summary>
    decimal AvgTransactionAmount,
    /// <summary>Number of distinct product categories purchased</summary>
    int CategoryDiversity,
    /// <summary>Days since most recent transaction</summary>
    int DaysSinceLastPurchase,
    /// <summary>Number of transactions in the observation window</summary>
    int TransactionCount,
    /// <summary>Ratio of flagged to total transactions (fraud signal)</summary>
    double FlaggedRatio
);
```

### 3. Magic Numbers & Hardcoded Thresholds

Thresholds in model logic MUST be configurable and documented.

```csharp
// ❌ Bad: Hardcoded magic numbers
if (totalSpend > 1000)
    return new SegmentPrediction(customerId, "High Value", 0.89, features);

// ✅ Good: Configurable with documentation
public class SegmentationConfig
{
    /// <summary>Minimum total spend to qualify for High Value segment</summary>
    public decimal HighValueThreshold { get; init; } = 1000m;

    /// <summary>Minimum purchase count to qualify as Regular</summary>
    public int RegularFrequencyThreshold { get; init; } = 3;

    /// <summary>Maximum average spend before At Risk classification</summary>
    public decimal AtRiskAvgSpendCeiling { get; init; } = 50m;
}
```

### 4. Model Evaluation

Every model MUST report these metrics before deployment:

| Metric Category | Required Metrics | Why |
|----------------|-----------------|-----|
| Classification | Precision, Recall, F1 per segment | Accuracy alone hides class imbalance |
| Confidence | Calibration curve, Brier score | Confidence scores must be meaningful |
| Stability | Cross-validation variance | Low variance = reliable predictions |
| Business | Revenue impact, segment migration rates | Technical metrics ≠ business value |

```csharp
// ✅ Good: Per-segment evaluation
public record ModelEvaluation(
    string ModelVersion,
    DateTime EvaluatedAt,
    Dictionary<string, SegmentMetrics> PerSegmentMetrics,
    double OverallAccuracy,
    int TestSetSize
);

public record SegmentMetrics(
    string SegmentName,
    double Precision,
    double Recall,
    double F1Score,
    int SupportCount
);
```

### 5. Bias & Fairness

Check for unintended discrimination across protected groups.

| Check | What to Verify |
|-------|---------------|
| Demographic parity | Segment distribution similar across store regions |
| Equal opportunity | Prediction accuracy consistent across customer cohorts |
| Feature audit | No proxy variables for protected attributes |
| Outcome review | "At Risk" classification doesn't disproportionately affect any group |

```csharp
// ✅ Good: Fairness check across store regions
public async Task<Dictionary<string, Dictionary<string, int>>> CheckSegmentDistributionByStoreAsync()
{
    var results = await _db.Transactions
        .GroupBy(t => t.StoreId)
        .Select(g => new
        {
            StoreId = g.Key,
            Customers = g.Select(t => t.CustomerId).Distinct().ToList()
        })
        .ToListAsync();

    var distribution = new Dictionary<string, Dictionary<string, int>>();
    foreach (var store in results)
    {
        var segmentCounts = new Dictionary<string, int>();
        foreach (var customerId in store.Customers)
        {
            var prediction = await PredictSegmentAsync(customerId);
            segmentCounts[prediction.PredictedSegment] =
                segmentCounts.GetValueOrDefault(prediction.PredictedSegment) + 1;
        }
        distribution[store.StoreId] = segmentCounts;
    }

    return distribution;
}
```

### 6. Reproducibility

| Requirement | Convention |
|------------|-----------|
| Random seeds | Always set and log seeds for any randomized operation |
| Model versioning | Version string in format `v{major}.{minor}.{patch}_{date}` |
| Data snapshots | Log the exact query/filter used to create training data |
| Environment | Pin all ML library versions in project file |
| Experiment tracking | Log hyperparameters, metrics, and data hash for every run |

```csharp
// ✅ Good: Reproducible prediction with versioning
public class SegmentationModel
{
    public const string ModelVersion = "v1.2.0_20260217";

    // Pin the seed for reproducible results
    private const int RandomSeed = 42;

    public SegmentPrediction Predict(CustomerFeatures features)
    {
        // Model logic with deterministic behavior...
    }
}
```

### 7. Production Readiness

Before deploying any model, verify:

| Category | Check |
|----------|-------|
| Performance | Prediction latency < 100ms at p99 |
| Fallback | Graceful degradation when model fails (default segment) |
| Monitoring | Prediction distribution logged for drift detection |
| A/B testing | Shadow mode before full rollout |
| Rollback | Previous model version can be restored instantly |

```csharp
// ✅ Good: Production-safe prediction with fallback and monitoring
public async Task<SegmentPrediction> PredictSegmentSafeAsync(
    string customerId,
    CancellationToken ct = default)
{
    try
    {
        var prediction = await PredictSegmentAsync(customerId, ct);

        // Monitor: log prediction distribution for drift detection
        _metrics.RecordPrediction(prediction.PredictedSegment, prediction.Confidence);

        // Alert on low confidence
        if (prediction.Confidence < 0.5)
            _logger.LogWarning(
                "Low confidence prediction for {CustomerId}: {Segment} ({Confidence:P0})",
                customerId, prediction.PredictedSegment, prediction.Confidence);

        return prediction;
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Prediction failed for {CustomerId}, using fallback", customerId);

        // Fallback: return safe default rather than throwing
        return new SegmentPrediction(customerId, "Regular", 0.0, ["fallback_error"]);
    }
}
```

### 8. Data Drift Monitoring

Track input feature distributions over time to detect model staleness.

```csharp
public record DriftReport(
    string ModelVersion,
    DateTime CheckedAt,
    Dictionary<string, DriftMetric> FeatureDrift
);

public record DriftMetric(
    string FeatureName,
    double BaselineMean,
    double CurrentMean,
    double PsiScore,       // Population Stability Index
    bool DriftDetected     // PSI > 0.2 = significant drift
);
```

| PSI Range | Interpretation | Action |
|-----------|---------------|--------|
| < 0.1 | No drift | None |
| 0.1 – 0.2 | Moderate drift | Monitor closely |
| > 0.2 | Significant drift | Retrain model |

## Review Checklist

When reviewing ML model code, verify:

- [ ] No data leakage (target, temporal, train-test, or group)
- [ ] Train-test split is group-aware (by customer, not by record)
- [ ] Temporal ordering respected (no future data in features)
- [ ] All thresholds configurable, not hardcoded magic numbers
- [ ] Features documented with business meaning
- [ ] Null/missing value strategy explicit per feature
- [ ] Per-class metrics reported (not just overall accuracy)
- [ ] Confidence scores calibrated and meaningful
- [ ] Bias checks across relevant dimensions (store, region, cohort)
- [ ] Random seeds set and logged for reproducibility
- [ ] Model version tracked in code and predictions
- [ ] Fallback behavior defined for prediction failures
- [ ] Prediction distribution logged for drift monitoring
- [ ] `CancellationToken` passed through async prediction paths
