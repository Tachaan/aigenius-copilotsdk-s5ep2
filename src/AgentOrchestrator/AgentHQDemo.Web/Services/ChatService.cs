using System.Net.Http.Json;
using System.Text.Json;
using System.Net.Http;

namespace AgentHQDemo.Web.Services;

public class ChatService(HttpClient http)
{
    private readonly HttpClient _http = http;

    public static readonly Dictionary<string, string> AvailableModels = new()
    {
        ["claude-haiku-4.5"] = "Claude Haiku 4.5 ⚡",
        ["gpt-4.1"] = "GPT-4.1",
        ["gpt-5"] = "GPT-5",
        ["claude-sonnet-4.5"] = "Claude Sonnet 4.5",
        ["claude-opus-4.5"] = "Claude Opus 4.5",
        ["gemini-2.5-pro"] = "Gemini 2.5 Pro"
    };

    /// <summary>
    /// Loads the models the API reports as available. Falls back to the static
    /// list if the API cannot be reached.
    /// </summary>
    public async Task<Dictionary<string, string>> GetModelsAsync()
    {
        try
        {
            var models = await _http.GetFromJsonAsync<List<ApiModel>>("/api/chat/models");
            if (models is { Count: > 0 })
            {
                return models
                    .Where(m => !string.IsNullOrWhiteSpace(m.Id))
                    .ToDictionary(m => m.Id!, m => string.IsNullOrWhiteSpace(m.Name) ? m.Id! : m.Name!);
            }
        }
        catch
        {
            // Fall through to the static catalog below.
        }

        return AvailableModels;
    }

    private sealed record ApiModel(string? Id, string? Name, string? Description);

    public async IAsyncEnumerable<string> StreamChatAsync(
        string prompt,
        string model = "claude-haiku-4.5",
        string? systemMessage = null)
    {
        var request = new
        {
            prompt,
            model,
            systemMessage = systemMessage ?? "You are a retail analytics assistant for a major grocery retailer. You help business analysts and data teams understand customer transaction patterns, segment performance, and retail insights. Answer questions about customer spending, product categories, store performance, and segment trends. Use this context: 5 customers (C001-C005), 4 segments (High Value, Regular, At Risk, New), 4 product categories (Grocery, Electronics, Fashion, Health), 4 stores (S001-S004). Provide business insights with data-driven reasoning. Format responses with markdown tables and bullet points. Never modify code or suggest code changes."
        };

        // Use ResponseHeadersRead to start streaming as soon as headers arrive
        var httpRequest = new HttpRequestMessage(HttpMethod.Post, "/api/chat/stream")
        {
            Content = JsonContent.Create(request)
        };
        using var response = await _http.SendAsync(httpRequest, HttpCompletionOption.ResponseHeadersRead);
        response.EnsureSuccessStatusCode();

        using var stream = await response.Content.ReadAsStreamAsync();
        using var reader = new StreamReader(stream);

        string? line;
        while ((line = await reader.ReadLineAsync()) is not null)
        {
            if (string.IsNullOrEmpty(line)) continue;

            if (line.StartsWith("data: "))
            {
                var data = line[6..];
                if (data == "[DONE]") yield break;

                string? chunk = null;
                try
                {
                    var json = JsonDocument.Parse(data);
                    if (json.RootElement.TryGetProperty("content", out var content))
                    {
                        chunk = content.GetString() ?? "";
                    }
                    if (json.RootElement.TryGetProperty("error", out var error))
                    {
                        throw new Exception(error.GetString());
                    }
                }
                catch (JsonException)
                {
                    // Ignore incomplete chunks
                }

                if (chunk is not null)
                {
                    yield return chunk;
                }
            }
        }
    }

    public async Task<bool> HealthCheckAsync()
    {
        try
        {
            var response = await _http.GetAsync("/api/chat/health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}
