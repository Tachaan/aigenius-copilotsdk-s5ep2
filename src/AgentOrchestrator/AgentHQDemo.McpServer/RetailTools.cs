using System.ComponentModel;
using AgentHQDemo.Api.Data;
using AgentHQDemo.Api.Models;
using AgentHQDemo.Api.Services;
using Microsoft.EntityFrameworkCore;
using ModelContextProtocol.Server;

namespace AgentHQDemo.McpServer;

/// <summary>
/// Read-only domain tools over the retail database.
/// </summary>
/// <remarks>
/// The model gets <c>get_customer_summary</c>, not <c>run_query</c>. The tool
/// surface is the security boundary, so there is no arbitrary-SQL escape hatch
/// to reason about. Mirrors <c>mcp_server/server.py</c> in the Python track.
/// </remarks>
[McpServerToolType]
public static class RetailTools
{
    /// <summary>
    /// Cap on rows returned by a single call, so a broad question cannot pull
    /// the whole table into the model's context window.
    /// </summary>
    private const int MaxLimit = 200;

    /// <summary>
    /// Resolves the database file, honouring the RETAIL_DB_PATH override.
    /// </summary>
    public static string ResolveDatabasePath()
    {
        var overridePath = Environment.GetEnvironmentVariable("RETAIL_DB_PATH");
        if (!string.IsNullOrWhiteSpace(overridePath))
        {
            return Path.GetFullPath(overridePath);
        }

        var local = Path.Combine(Directory.GetCurrentDirectory(), "retail.db");
        if (File.Exists(local))
        {
            return local;
        }

        // Fall back to the API project's copy so the server can be launched
        // from anywhere in the repo during a lab.
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir != null; dir = dir.Parent)
        {
            var candidate = Path.Combine(dir.FullName, "AgentHQDemo.Api", "retail.db");
            if (File.Exists(candidate))
            {
                return candidate;
            }
        }

        return local;
    }

    [McpServerTool(Name = "list_transactions", ReadOnly = true, Destructive = false)]
    [Description("Lists retail transactions, most recent first. Optionally filter to a single customer.")]
    public static async Task<IReadOnlyList<TransactionDto>> ListTransactionsAsync(
        IDbContextFactory<RetailDbContext> dbFactory,
        [Description("Optional customer id to filter by, for example C003.")] string? customerId = null,
        [Description("Maximum rows to return (1-200).")] int limit = 50,
        CancellationToken cancellationToken = default)
    {
        var capped = Math.Clamp(limit, 1, MaxLimit);
        await using var db = await dbFactory.CreateDbContextAsync(cancellationToken);

        var query = db.Transactions.AsNoTracking();
        if (!string.IsNullOrWhiteSpace(customerId))
        {
            query = query.Where(t => t.CustomerId == customerId);
        }

        var rows = await query
            .OrderByDescending(t => t.Timestamp)
            .Take(capped)
            .ToListAsync(cancellationToken);

        return [.. rows.Select(TransactionDto.From)];
    }

    [McpServerTool(Name = "get_transaction", ReadOnly = true, Destructive = false)]
    [Description("Gets a single retail transaction by its numeric id.")]
    public static async Task<TransactionDto?> GetTransactionAsync(
        IDbContextFactory<RetailDbContext> dbFactory,
        [Description("The transaction id.")] int transactionId,
        CancellationToken cancellationToken = default)
    {
        await using var db = await dbFactory.CreateDbContextAsync(cancellationToken);
        var txn = await db.Transactions.AsNoTracking()
            .FirstOrDefaultAsync(t => t.Id == transactionId, cancellationToken);

        return txn is null ? null : TransactionDto.From(txn);
    }

    [McpServerTool(Name = "list_segments", ReadOnly = true, Destructive = false)]
    [Description("Lists the customer segments with their size, average monthly spend and retention rate.")]
    public static async Task<IReadOnlyList<SegmentDto>> ListSegmentsAsync(
        IDbContextFactory<RetailDbContext> dbFactory,
        CancellationToken cancellationToken = default)
    {
        await using var db = await dbFactory.CreateDbContextAsync(cancellationToken);
        var rows = await db.Segments.AsNoTracking().ToListAsync(cancellationToken);
        return [.. rows.Select(SegmentDto.From)];
    }

    [McpServerTool(Name = "get_customer_summary", ReadOnly = true, Destructive = false)]
    [Description("Summarises one customer's spending: total, average, transaction count and the categories they buy from.")]
    public static async Task<CustomerSummaryDto> GetCustomerSummaryAsync(
        IDbContextFactory<RetailDbContext> dbFactory,
        [Description("The customer id, for example C003.")] string customerId,
        CancellationToken cancellationToken = default)
    {
        await using var db = await dbFactory.CreateDbContextAsync(cancellationToken);
        var rows = await db.Transactions.AsNoTracking()
            .Where(t => t.CustomerId == customerId)
            .ToListAsync(cancellationToken);

        if (rows.Count == 0)
        {
            return new CustomerSummaryDto(customerId, 0, 0m, 0m, [], null, null);
        }

        var total = rows.Sum(t => t.Amount);
        return new CustomerSummaryDto(
            customerId,
            rows.Count,
            Math.Round(total, 2),
            Math.Round(total / rows.Count, 2),
            [.. rows.Select(t => t.ProductCategory).Distinct().Order()],
            rows.Min(t => t.Timestamp),
            rows.Max(t => t.Timestamp));
    }

    [McpServerTool(Name = "predict_segment", ReadOnly = true, Destructive = false)]
    [Description("Predicts which segment a customer belongs to, with a confidence score and the features behind the call.")]
    public static async Task<SegmentPrediction> PredictSegmentAsync(
        IDbContextFactory<RetailDbContext> dbFactory,
        [Description("The customer id, for example C003.")] string customerId,
        CancellationToken cancellationToken = default)
    {
        // Reuses the API's own scoring logic rather than reimplementing it, so
        // the chat and the REST endpoint can never disagree about a customer.
        await using var db = await dbFactory.CreateDbContextAsync(cancellationToken);
        return await new RetailAnalyticsService(db).PredictSegmentAsync(customerId);
    }
}

/// <summary>Shapes a row the same way the REST API does, so the model sees one contract.</summary>
public record TransactionDto(
    int Id,
    string CustomerId,
    decimal Amount,
    string ProductCategory,
    string StoreId,
    DateTime Timestamp,
    bool IsFlagged)
{
    public static TransactionDto From(Transaction t) =>
        new(t.Id, t.CustomerId, t.Amount, t.ProductCategory, t.StoreId, t.Timestamp, t.IsFlagged);
}

public record SegmentDto(
    int Id,
    string Name,
    string Description,
    int CustomerCount,
    decimal AvgMonthlySpend,
    decimal RetentionRate)
{
    public static SegmentDto From(CustomerSegment s) =>
        new(s.Id, s.Name, s.Description, s.CustomerCount, s.AvgMonthlySpend, s.RetentionRate);
}

public record CustomerSummaryDto(
    string CustomerId,
    int TransactionCount,
    decimal TotalSpend,
    decimal AverageSpend,
    string[] Categories,
    DateTime? FirstPurchase,
    DateTime? LastPurchase);
