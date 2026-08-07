using AgentHQDemo.Api.Data;
using AgentHQDemo.Api.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddOpenApi();

// Add CORS for Blazor WebAssembly
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Register database and application services
builder.Services.AddDbContext<RetailDbContext>(options =>
    options.UseSqlite("Data Source=retail.db"));
builder.Services.AddScoped<RetailAnalyticsService>();
builder.Services.AddSingleton<CopilotChatService>();

var app = builder.Build();

// Seed database on startup
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<RetailDbContext>();
    await db.Database.EnsureCreatedAsync();
    var service = scope.ServiceProvider.GetRequiredService<RetailAnalyticsService>();
    await service.SeedDataAsync();
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseCors();

// Serve static files (Chat UI)
app.UseDefaultFiles();
app.UseStaticFiles();

app.MapControllers();

app.Run();
