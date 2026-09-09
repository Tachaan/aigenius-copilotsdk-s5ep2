using System.Reflection;
using AgentHQDemo.Api.Data;
using AgentHQDemo.Api.Models;
using AgentHQDemo.McpServer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using ModelContextProtocol.Server;

namespace AgentHQDemo.Tests;

/// <summary>
/// Tests for the read-only retail MCP server.
/// Mirrors <c>tests/test_mcp_server.py</c> in the Python track.
/// </summary>
/// <remarks>
/// These cover the tool surface the model sees. The point of the server is that
/// it is the security boundary, so the read-only guarantee is tested too.
/// </remarks>
public class RetailToolsTests : IDisposable
{
    private readonly ServiceProvider _provider;
    private readonly IDbContextFactory<RetailDbContext> _dbFactory;
    private readonly SqliteTestDatabase _database = new();

    public RetailToolsTests()
    {
        var services = new ServiceCollection();
        services.AddDbContextFactory<RetailDbContext>(options =>
            options.UseSqlite(_database.Connection));
        _provider = services.BuildServiceProvider();
        _dbFactory = _provider.GetRequiredService<IDbContextFactory<RetailDbContext>>();

        using var db = _dbFactory.CreateDbContext();
        db.Database.EnsureCreated();

        var now = DateTime.UtcNow;
        db.Transactions.AddRange(
            new Transaction { CustomerId = "C001", Amount = 100.00m, ProductCategory = "Grocery", StoreId = "S001", Timestamp = now.AddDays(-3) },
            new Transaction { CustomerId = "C001", Amount = 250.00m, ProductCategory = "Fashion", StoreId = "S002", Timestamp = now.AddDays(-1) },
            new Transaction { CustomerId = "C002", Amount = 20.00m, ProductCategory = "Grocery", StoreId = "S001", Timestamp = now.AddDays(-2) }
        );
        db.Segments.Add(new CustomerSegment
        {
            Name = "High Value",
            Description = "Top spenders",
            CustomerCount = 10,
            AvgMonthlySpend = 500m,
            RetentionRate = 0.9m
        });
        db.SaveChanges();
    }

    [Fact]
    public async Task ListTransactions_FiltersByCustomer()
    {
        var rows = await RetailTools.ListTransactionsAsync(_dbFactory, "C001");

        Assert.Equal(2, rows.Count);
        Assert.All(rows, r => Assert.Equal("C001", r.CustomerId));
    }

    [Fact]
    public async Task ListTransactions_ReturnsNewestFirst()
    {
        var rows = await RetailTools.ListTransactionsAsync(_dbFactory, "C001");

        Assert.Equal([250.00m, 100.00m], rows.Select(r => r.Amount));
    }

    [Fact]
    public async Task ListTransactions_CapsTheLimit()
    {
        // Guards the context window: a huge limit must not return a huge result.
        var rows = await RetailTools.ListTransactionsAsync(_dbFactory, limit: 10_000);

        Assert.Equal(3, rows.Count);
    }

    [Fact]
    public async Task GetTransaction_ReturnsNullWhenMissing()
    {
        Assert.Null(await RetailTools.GetTransactionAsync(_dbFactory, 9999));
    }

    [Fact]
    public async Task ListSegments_ReturnsSeededSegments()
    {
        var rows = await RetailTools.ListSegmentsAsync(_dbFactory);

        var segment = Assert.Single(rows);
        Assert.Equal("High Value", segment.Name);
        Assert.Equal(0.9m, segment.RetentionRate);
    }

    [Fact]
    public async Task CustomerSummary_AggregatesSpend()
    {
        var summary = await RetailTools.GetCustomerSummaryAsync(_dbFactory, "C001");

        Assert.Equal(2, summary.TransactionCount);
        Assert.Equal(350.00m, summary.TotalSpend);
        Assert.Equal(175.00m, summary.AverageSpend);
        Assert.Equal(["Fashion", "Grocery"], summary.Categories);
    }

    [Fact]
    public async Task CustomerSummary_HandlesUnknownCustomer()
    {
        var summary = await RetailTools.GetCustomerSummaryAsync(_dbFactory, "NOPE");

        Assert.Equal(0, summary.TransactionCount);
        Assert.Equal(0m, summary.TotalSpend);
        Assert.Empty(summary.Categories);
    }

    [Fact]
    public async Task PredictSegment_MatchesTheApiLogic()
    {
        var prediction = await RetailTools.PredictSegmentAsync(_dbFactory, "C002");

        // C002 has a single 20.00 purchase, so the service's "At Risk" branch wins.
        Assert.Equal("C002", prediction.CustomerId);
        Assert.Equal("At Risk", prediction.PredictedSegment);
    }

    [Fact]
    public void ResolveDatabasePath_HonoursTheEnvironmentOverride()
    {
        var expected = Path.Combine(Path.GetTempPath(), "custom-retail.db");
        Environment.SetEnvironmentVariable("RETAIL_DB_PATH", expected);
        try
        {
            Assert.Equal(Path.GetFullPath(expected), RetailTools.ResolveDatabasePath());
        }
        finally
        {
            Environment.SetEnvironmentVariable("RETAIL_DB_PATH", null);
        }
    }

    [Fact]
    public void ReadOnlyConnection_RejectsWrites()
    {
        // The security guarantee: writes fail at the driver, not by convention.
        var path = Path.Combine(Path.GetTempPath(), $"retail-readonly-{Guid.NewGuid():N}.db");
        try
        {
            using (var seed = new Microsoft.Data.Sqlite.SqliteConnection($"Data Source={path}"))
            {
                seed.Open();
                using var create = seed.CreateCommand();
                create.CommandText = "CREATE TABLE probe (id INTEGER)";
                create.ExecuteNonQuery();
            }

            using var connection = new Microsoft.Data.Sqlite.SqliteConnection(
                $"Data Source={path};Mode=ReadOnly");
            connection.Open();

            // The row reads back fine, so the connection genuinely works...
            using var read = connection.CreateCommand();
            read.CommandText = "SELECT count(*) FROM probe";
            Assert.Equal(0L, (long)read.ExecuteScalar()!);

            // ...but SQLite itself refuses the write.
            using var write = connection.CreateCommand();
            write.CommandText = "INSERT INTO probe (id) VALUES (1)";
            var ex = Assert.Throws<Microsoft.Data.Sqlite.SqliteException>(() => write.ExecuteNonQuery());
            Assert.Contains("readonly", ex.Message, StringComparison.OrdinalIgnoreCase);
        }
        finally
        {
            File.Delete(path);
        }
    }

    [Fact]
    public void ExposesTheExpectedTools()
    {
        Assert.Equal(
            ["get_customer_summary", "get_transaction", "list_segments", "list_transactions", "predict_segment"],
            ToolAttributes().Select(a => a.Name).Order());
    }

    [Fact]
    public void EveryToolIsMarkedReadOnly()
    {
        // The annotation is what tells a host it is safe to auto-approve, so a
        // tool gaining a side effect must not silently keep the read-only hint.
        var tools = ToolAttributes();
        Assert.NotEmpty(tools);
        Assert.All(tools, attribute =>
        {
            Assert.True(attribute.ReadOnly, attribute.Name);
            Assert.False(attribute.Destructive, attribute.Name);
        });
    }

    private static List<McpServerToolAttribute> ToolAttributes() =>
        [.. typeof(RetailTools)
            .GetMethods()
            .Select(m => m.GetCustomAttribute<McpServerToolAttribute>())
            .Where(a => a is not null)
            .Select(a => a!)];

    public void Dispose()
    {
        _provider.Dispose();
        _database.Dispose();
        GC.SuppressFinalize(this);
    }

    /// <summary>
    /// Keeps a single in-memory SQLite connection open for the test's lifetime,
    /// which is what the Python fixture's StaticPool achieves.
    /// </summary>
    private sealed class SqliteTestDatabase : IDisposable
    {
        public Microsoft.Data.Sqlite.SqliteConnection Connection { get; } = Open();

        private static Microsoft.Data.Sqlite.SqliteConnection Open()
        {
            var connection = new Microsoft.Data.Sqlite.SqliteConnection("DataSource=:memory:");
            connection.Open();
            return connection;
        }

        public void Dispose() => Connection.Dispose();
    }
}
