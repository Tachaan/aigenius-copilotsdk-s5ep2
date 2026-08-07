using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using Blazored.LocalStorage;
using AgentHQDemo.Web;
using AgentHQDemo.Web.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Configure HttpClient for API calls
var apiBase = builder.Configuration["ApiBaseUrl"] ?? "http://localhost:5050";
builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(apiBase) });

// Register services
builder.Services.AddBlazoredLocalStorage();
builder.Services.AddScoped<ChatService>();
builder.Services.AddScoped<StorageService>();

await builder.Build().RunAsync();
