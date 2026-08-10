using AgentHQDemo.Api.Data;
using AgentHQDemo.Api.Services;
using Microsoft.EntityFrameworkCore;

namespace AgentHQDemo.Tests;

public class RetailAnalyticsServiceTests : IDisposable
{
    private readonly RetailDbContext _db;
    private readonly RetailAnalyticsService _service;

    public RetailAnalyticsServiceTests()
    {
        var options = new DbContextOptionsBuilder<RetailDbContext>()
            .UseSqlite("DataSource=:memory:")
            .Options;

        _db = new RetailDbContext(options);
        _db.Database.OpenConnection();
        _db.Database.EnsureCreated();

        _service = new RetailAnalyticsService(_db);
    }

    [Fact]
    public async Task SeedData_Creates10Transactions()
    {
        await _service.SeedDataAsync();

        var transactions = await _service.GetTransactionsAsync();
        Assert.Equal(10, transactions.Count);
    }

    [Fact]
    public async Task SeedData_Creates4Segments()
    {
        await _service.SeedDataAsync();

        var segments = await _service.GetSegmentsAsync();
        Assert.Equal(4, segments.Count);
        Assert.Contains(segments, s => s.Name == "High Value");
        Assert.Contains(segments, s => s.Name == "At Risk");
    }

    [Fact]
    public async Task AddTransaction_PersistsToDatabase()
    {
        var txn = new AgentHQDemo.Api.Models.Transaction
        {
            CustomerId = "C099",
            Amount = 100m,
            ProductCategory = "Grocery",
            StoreId = "S001"
        };

        var created = await _service.AddTransactionAsync(txn);

        Assert.True(created.Id > 0);
        var retrieved = await _service.GetTransactionAsync(created.Id);
        Assert.Equal("C099", retrieved.CustomerId);
    }

    [Fact]
    public async Task PredictSegment_HighSpender_ReturnsHighValue()
    {
        await _service.SeedDataAsync();

        var prediction = await _service.PredictSegmentAsync("C003");

        Assert.Equal("High Value", prediction.PredictedSegment);
        Assert.True(prediction.Confidence > 0.5);
    }

    [Fact]
    public async Task PredictSegment_UnknownCustomer_ReturnsNew()
    {
        var prediction = await _service.PredictSegmentAsync("C999");

        Assert.Equal("New", prediction.PredictedSegment);
    }

    public void Dispose()
    {
        _db.Database.CloseConnection();
        _db.Dispose();
    }
}
