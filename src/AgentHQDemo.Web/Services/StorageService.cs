using Blazored.LocalStorage;

namespace AgentHQDemo.Web.Services;

public record ChatMessage(string Content, bool IsUser, DateTime Timestamp);

public class StorageService(ILocalStorageService localStorage)
{
    private readonly ILocalStorageService _localStorage = localStorage;
    private const string MessagesKey = "chat_messages";
    private const string ThemeKey = "theme";
    private const string ModelKey = "selected_model";

    public async Task<List<ChatMessage>> LoadMessagesAsync()
    {
        try
        {
            return await _localStorage.GetItemAsync<List<ChatMessage>>(MessagesKey) ?? [];
        }
        catch
        {
            return [];
        }
    }

    public async Task SaveMessagesAsync(List<ChatMessage> messages)
    {
        await _localStorage.SetItemAsync(MessagesKey, messages);
    }

    public async Task ClearMessagesAsync()
    {
        await _localStorage.RemoveItemAsync(MessagesKey);
    }

    public async Task<string> GetThemeAsync()
    {
        try
        {
            return await _localStorage.GetItemAsync<string>(ThemeKey) ?? "dark";
        }
        catch
        {
            return "dark";
        }
    }

    public async Task SetThemeAsync(string theme)
    {
        await _localStorage.SetItemAsync(ThemeKey, theme);
    }

    public async Task<string> GetSelectedModelAsync()
    {
        try
        {
            return await _localStorage.GetItemAsync<string>(ModelKey) ?? "claude-haiku-4.5";
        }
        catch
        {
            return "claude-haiku-4.5";
        }
    }

    public async Task SetSelectedModelAsync(string model)
    {
        await _localStorage.SetItemAsync(ModelKey, model);
    }
}
