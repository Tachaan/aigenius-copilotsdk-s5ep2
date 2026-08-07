namespace AgentHQDemo.Api.Models;

/// <summary>
/// A customer segment grouping for analytics.
/// </summary>
public class CustomerSegment
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public int CustomerCount { get; set; }
    public decimal AvgMonthlySpend { get; set; }
    public decimal RetentionRate { get; set; }
}
