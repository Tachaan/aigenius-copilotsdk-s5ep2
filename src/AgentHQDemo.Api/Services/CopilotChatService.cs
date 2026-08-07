using GitHub.Copilot.SDK;

namespace AgentHQDemo.Api.Services;

/// <summary>
/// Service for managing Copilot chat sessions.
/// Demonstrates GitHub Copilot SDK integration for the Three Mondays demo.
/// </summary>
public class CopilotChatService : IAsyncDisposable
{
    private readonly ILogger<CopilotChatService> _logger;
    private CopilotClient? _client;
    private bool _isStarted;

    public CopilotChatService(ILogger<CopilotChatService> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Ensures the Copilot client is started. Recreates if connection was lost.
    /// </summary>
    public async Task EnsureStartedAsync()
    {
        if (_isStarted && _client != null) return;

        // Reset in case of a previous failed connection
        _isStarted = false;
        if (_client != null)
        {
            try { await _client.StopAsync(); } catch { /* ignore cleanup errors */ }
        }

        _client = new CopilotClient();
        await _client.StartAsync();
        _isStarted = true;
        _logger.LogInformation("Copilot client started");
    }

    /// <summary>
    /// Sends a chat message and streams the response.
    /// </summary>
    public async IAsyncEnumerable<string> ChatStreamAsync(
        string prompt,
        string model = "claude-haiku-4.5",
        string? systemMessage = null,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await EnsureStartedAsync();

        if (_client == null)
        {
            yield return "Error: Copilot client not initialized";
            yield break;
        }

        _logger.LogInformation("Creating session with model: {Model}", model);

        var outputChannel = System.Threading.Channels.Channel.CreateUnbounded<string>();

        // Run the Copilot session in a background task so we can yield outside try/catch
        _ = Task.Run(async () =>
        {
            try
            {
                SessionConfig config = new()
                {
                    Model = model,
                    Streaming = true,
                    SystemMessage = systemMessage != null ? new SystemMessageConfig
                    {
                        Mode = SystemMessageMode.Append,
                        Content = systemMessage
                    } : null
                };

                await using var session = await _client.CreateSessionAsync(config);
                var done = new TaskCompletionSource();

                session.On(evt =>
                {
                    switch (evt)
                    {
                        case AssistantMessageDeltaEvent delta:
                            outputChannel.Writer.TryWrite(delta.Data.DeltaContent ?? "");
                            break;
                        case AssistantMessageEvent msg:
                            _logger.LogInformation("Assistant response complete: {Length} chars", msg.Data.Content?.Length ?? 0);
                            break;
                        case SessionIdleEvent:
                            done.SetResult();
                            break;
                        case SessionErrorEvent error:
                            _logger.LogError("Session error: {Message}", error.Data.Message);
                            done.SetException(new Exception(error.Data.Message));
                            break;
                    }
                });

                await session.SendAsync(new MessageOptions { Prompt = prompt });
                await done.Task;
                outputChannel.Writer.Complete();
            }
            catch (IOException ex)
            {
                _logger.LogWarning("Copilot connection lost: {Message}", ex.Message);
                _isStarted = false;
                outputChannel.Writer.Complete(ex);
            }
            catch (Exception ex)
            {
                outputChannel.Writer.Complete(ex);
            }
        }, cancellationToken);

        await foreach (var chunk in outputChannel.Reader.ReadAllAsync(cancellationToken))
        {
            yield return chunk;
        }
    }

    /// <summary>
    /// Sends a chat message and returns the complete response.
    /// </summary>
    public async Task<string> ChatAsync(
        string prompt, 
        string model = "claude-haiku-4.5",
        string? systemMessage = null, 
        CancellationToken cancellationToken = default)
    {
        var response = new System.Text.StringBuilder();
        await foreach (var chunk in ChatStreamAsync(prompt, model, systemMessage, cancellationToken))
        {
            response.Append(chunk);
        }
        return response.ToString();
    }

    public async ValueTask DisposeAsync()
    {
        if (_client != null)
        {
            await _client.StopAsync();
            _logger.LogInformation("Copilot client stopped");
        }
    }
}
