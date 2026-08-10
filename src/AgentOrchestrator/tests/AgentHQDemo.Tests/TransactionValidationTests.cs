using System.ComponentModel.DataAnnotations;
using AgentHQDemo.Api.Models;

namespace AgentHQDemo.Tests;

public class TransactionValidationTests
{
    private static List<ValidationResult> ValidateModel(Transaction transaction)
    {
        var validationResults = new List<ValidationResult>();
        var validationContext = new ValidationContext(transaction);
        Validator.TryValidateObject(transaction, validationContext, validationResults, true);
        return validationResults;
    }

    [Fact]
    public void ValidTransaction_PassesValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = 100.50m,
            ProductCategory = "Electronics",
            StoreId = "S001",
            Timestamp = DateTime.UtcNow
        };

        var results = ValidateModel(transaction);

        Assert.Empty(results);
    }

    [Fact]
    public void Transaction_WithEmptyCustomerId_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "",
            Amount = 100.50m,
            ProductCategory = "Electronics",
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("CustomerId"));
    }

    [Fact]
    public void Transaction_WithNegativeAmount_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = -10.00m,
            ProductCategory = "Electronics",
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("Amount"));
    }

    [Fact]
    public void Transaction_WithZeroAmount_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = 0m,
            ProductCategory = "Electronics",
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("Amount"));
    }

    [Fact]
    public void Transaction_WithAmountTooHigh_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = 1000001m,
            ProductCategory = "Electronics",
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("Amount"));
    }

    [Fact]
    public void Transaction_WithEmptyProductCategory_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = 100.50m,
            ProductCategory = "",
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("ProductCategory"));
    }

    [Fact]
    public void Transaction_WithEmptyStoreId_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = 100.50m,
            ProductCategory = "Electronics",
            StoreId = ""
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("StoreId"));
    }

    [Fact]
    public void Transaction_WithTooLongCustomerId_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = new string('A', 101), // 101 characters
            Amount = 100.50m,
            ProductCategory = "Electronics",
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("CustomerId"));
    }

    [Fact]
    public void Transaction_WithTooLongProductCategory_FailsValidation()
    {
        var transaction = new Transaction
        {
            CustomerId = "C001",
            Amount = 100.50m,
            ProductCategory = new string('A', 51), // 51 characters
            StoreId = "S001"
        };

        var results = ValidateModel(transaction);

        Assert.NotEmpty(results);
        Assert.Contains(results, r => r.ErrorMessage != null && r.ErrorMessage.Contains("ProductCategory"));
    }
}
