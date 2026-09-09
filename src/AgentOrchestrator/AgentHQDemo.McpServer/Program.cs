using AgentHQDemo.Api.Data;
using AgentHQDemo.McpServer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

// Read-only MCP server over the retail SQLite database.
//
// Why this exists: CopilotChatService used to send prompts with no access to the
// application's own data, so the chat could not answer "who are my highest
// spending customers?". This server closes that gap with a small set of
// read-only domain tools.
//
// The REST API keeps its direct EF Core access through RetailAnalyticsService —
// MCP is for the *model*, not for the application talking to its own database.
//
// Mirrors mcp_server/server.py in the Python track.

var builder = Host.CreateApplicationBuilder(args);

// stdio carries the MCP protocol on stdout, so every log must go to stderr.
// A stray Console.WriteLine here corrupts the protocol stream.
builder.Logging.AddConsole(options =>
{
    options.LogToStandardErrorThreshold = LogLevel.Trace;
});

var dbPath = RetailTools.ResolveDatabasePath();
if (!File.Exists(dbPath))
{
    await Console.Error.WriteLineAsync(
        $"Retail database not found at {dbPath}. Start the API once " +
        "(dotnet run --project src/AgentOrchestrator/AgentHQDemo.Api) to create and seed it.");
    return 1;
}

// Mode=ReadOnly is enforced by SQLite itself, so this is a stronger guarantee
// than merely not writing any INSERT statements in the tool bodies. Even a
// prompt-injected instruction to modify data cannot succeed.
builder.Services.AddDbContextFactory<RetailDbContext>(options =>
    options.UseSqlite($"Data Source={dbPath};Mode=ReadOnly"));

builder.Services
    .AddMcpServer(options => options.ServerInfo = new() { Name = "retail-analytics", Version = "1.0.0" })
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

await builder.Build().RunAsync();
return 0;
