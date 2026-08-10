using Microsoft.AspNetCore.Mvc;
using AgentHQDemo.Api.Models;
using AgentHQDemo.Api.Services;

namespace AgentHQDemo.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TransactionsController(RetailAnalyticsService service) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<List<Transaction>>> GetAll()
    {
        return Ok(await service.GetTransactionsAsync());
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<Transaction>> Get(int id)
    {
        var txn = await service.GetTransactionAsync(id);
        if (txn == null) return NotFound();
        return Ok(txn);
    }

    [HttpPost]
    public async Task<ActionResult<Transaction>> Create([FromBody] Transaction transaction)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var created = await service.AddTransactionAsync(transaction);
        return CreatedAtAction(nameof(Get), new { id = created.Id }, created);
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var deleted = await service.DeleteTransactionAsync(id);
        return deleted ? NoContent() : NotFound();
    }
}
