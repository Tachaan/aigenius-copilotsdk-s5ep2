using AgentHQDemo.Api.Data;
using AgentHQDemo.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace AgentHQDemo.Api.Services;

/// <summary>
/// Service for retail transaction analytics and customer segmentation.
/// Contains intentional issues for code review demonstrations.
/// </summary>
public class RetailAnalyticsService(RetailDbContext db)
{
    private readonly RetailDbContext _db = db;

    /// <summary>
    /// Returns all transactions with segment info.
    /// BUG: N+1 query — loops through each transaction to look up segment.
    /// </summary>
    public async Task<List<object>> GetTransactionsWithSegmentsAsync()
    {
        var transactions = await _db.Transactions.ToListAsync();
        var results = new List<object>();

        foreach (var txn in transactions)
        {
            // N+1: querying segments for every single transaction
            var segment = await PredictSegmentAsync(txn.CustomerId);
            results.Add(new { txn.Id, txn.CustomerId, txn.Amount, txn.ProductCategory, txn.StoreId, txn.Timestamp, txn.IsFlagged, segment.PredictedSegment });
        }

        return results;
    }

    public async Task<List<Transaction>> GetTransactionsAsync()
    {
        return await _db.Transactions.ToListAsync();
    }

    /// <summary>
    /// Returns a single transaction by ID.
    /// BUG: Missing null check — returns null without proper handling.
    /// </summary>
    public async Task<Transaction> GetTransactionAsync(int id)
    {
        // Missing null check: will return null if not found
        return (await _db.Transactions.FindAsync(id))!;
    }

    /// <summary>
    /// Adds a new transaction.
    /// BUG: No input validation — allows negative amounts and empty customer IDs.
    /// </summary>
    public async Task<Transaction> AddTransactionAsync(Transaction transaction)
    {
        // No validation: negative amounts and empty CustomerId are allowed
        transaction.Timestamp = DateTime.UtcNow;
        _db.Transactions.Add(transaction);
        await _db.SaveChangesAsync();
        return transaction;
    }

    public async Task<bool> DeleteTransactionAsync(int id)
    {
        var txn = await _db.Transactions.FindAsync(id);
        if (txn == null) return false;
        _db.Transactions.Remove(txn);
        await _db.SaveChangesAsync();
        return true;
    }

    public async Task<List<CustomerSegment>> GetSegmentsAsync()
    {
        return await _db.Segments.ToListAsync();
    }

    public async Task<CustomerSegment?> GetSegmentAsync(int id)
    {
        return await _db.Segments.FindAsync(id);
    }

    /// <summary>
    /// Predicts which segment a customer belongs to based on spending.
    /// BUG: Hardcoded magic number threshold (1000).
    /// </summary>
    public async Task<SegmentPrediction> PredictSegmentAsync(string customerId)
    {
        var transactions = await _db.Transactions
            .Where(t => t.CustomerId == customerId)
            .ToListAsync();

        if (transactions.Count == 0)
        {
            return new SegmentPrediction(customerId, "New", 0.5, ["no_history"]);
        }

        var totalSpend = transactions.Sum(t => t.Amount);
        var avgSpend = totalSpend / transactions.Count;
        var frequency = transactions.Count;

        // BUG: Hardcoded magic number — should be configurable
        if (totalSpend > 1000)
        {
            return new SegmentPrediction(customerId, "High Value", 0.89,
                ["high_total_spend", "multi_category", $"total_{totalSpend:F0}"]);
        }

        if (frequency >= 3)
        {
            return new SegmentPrediction(customerId, "Regular", 0.75,
                ["frequent_purchases", $"frequency_{frequency}", $"avg_{avgSpend:F0}"]);
        }

        if (avgSpend < 50)
        {
            return new SegmentPrediction(customerId, "At Risk", 0.62,
                ["low_avg_spend", $"avg_{avgSpend:F0}", $"total_{totalSpend:F0}"]);
        }

        return new SegmentPrediction(customerId, "Regular", 0.55,
            ["moderate_activity", $"total_{totalSpend:F0}"]);
    }

    /// <summary>
    /// Seeds the database with sample retail data.
    /// </summary>
    public async Task SeedDataAsync()
    {
        if (await _db.Transactions.AnyAsync()) return;

        _db.Transactions.AddRange(
            new Transaction { CustomerId = "C001", Amount = 245.50m, ProductCategory = "Grocery", StoreId = "S001", Timestamp = DateTime.UtcNow.AddDays(-30) },
            new Transaction { CustomerId = "C001", Amount = 89.99m, ProductCategory = "Electronics", StoreId = "S002", Timestamp = DateTime.UtcNow.AddDays(-25) },
            new Transaction { CustomerId = "C002", Amount = 32.00m, ProductCategory = "Grocery", StoreId = "S001", Timestamp = DateTime.UtcNow.AddDays(-20) },
            new Transaction { CustomerId = "C002", Amount = 15.50m, ProductCategory = "Health", StoreId = "S003", Timestamp = DateTime.UtcNow.AddDays(-18) },
            new Transaction { CustomerId = "C003", Amount = 1250.00m, ProductCategory = "Electronics", StoreId = "S002", Timestamp = DateTime.UtcNow.AddDays(-15) },
            new Transaction { CustomerId = "C003", Amount = 450.00m, ProductCategory = "Fashion", StoreId = "S004", Timestamp = DateTime.UtcNow.AddDays(-10) },
            new Transaction { CustomerId = "C004", Amount = 12.99m, ProductCategory = "Grocery", StoreId = "S001", Timestamp = DateTime.UtcNow.AddDays(-8) },
            new Transaction { CustomerId = "C004", Amount = 8.50m, ProductCategory = "Grocery", StoreId = "S001", Timestamp = DateTime.UtcNow.AddDays(-5) },
            new Transaction { CustomerId = "C005", Amount = 675.00m, ProductCategory = "Electronics", StoreId = "S002", Timestamp = DateTime.UtcNow.AddDays(-3) },
            new Transaction { CustomerId = "C005", Amount = 320.00m, ProductCategory = "Fashion", StoreId = "S004", Timestamp = DateTime.UtcNow.AddDays(-1) }
        );

        _db.Segments.AddRange(
            new CustomerSegment { Name = "High Value", Description = "Top 10% spenders with strong loyalty indicators", CustomerCount = 150, AvgMonthlySpend = 850m, RetentionRate = 0.92m },
            new CustomerSegment { Name = "Regular", Description = "Consistent monthly shoppers across categories", CustomerCount = 3200, AvgMonthlySpend = 180m, RetentionRate = 0.78m },
            new CustomerSegment { Name = "At Risk", Description = "Declining purchase frequency over past 90 days", CustomerCount = 890, AvgMonthlySpend = 95m, RetentionRate = 0.45m },
            new CustomerSegment { Name = "New", Description = "Joined within the last 90 days", CustomerCount = 420, AvgMonthlySpend = 120m, RetentionRate = 0.65m }
        );

        await _db.SaveChangesAsync();
    }
}
