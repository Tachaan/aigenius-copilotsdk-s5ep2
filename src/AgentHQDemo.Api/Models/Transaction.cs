using System.ComponentModel.DataAnnotations;

namespace AgentHQDemo.Api.Models;

/// <summary>
/// A retail purchase transaction.
/// </summary>
public class Transaction
{
    public int Id { get; set; }
    
    [Required(ErrorMessage = "CustomerId is required")]
    [StringLength(100, MinimumLength = 1, ErrorMessage = "CustomerId must be between 1 and 100 characters")]
    public string CustomerId { get; set; } = "";
    
    [Range(0.01, 1000000, ErrorMessage = "Amount must be between 0.01 and 1,000,000")]
    public decimal Amount { get; set; }
    
    [Required(ErrorMessage = "ProductCategory is required")]
    [StringLength(50, MinimumLength = 1, ErrorMessage = "ProductCategory must be between 1 and 50 characters")]
    public string ProductCategory { get; set; } = "";
    
    [Required(ErrorMessage = "StoreId is required")]
    [StringLength(50, MinimumLength = 1, ErrorMessage = "StoreId must be between 1 and 50 characters")]
    public string StoreId { get; set; } = "";
    
    public DateTime Timestamp { get; set; }
    public bool IsFlagged { get; set; }
}
