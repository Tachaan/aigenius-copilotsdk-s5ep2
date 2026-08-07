using Microsoft.AspNetCore.Mvc;
using AgentHQDemo.Api.Models;
using AgentHQDemo.Api.Services;

namespace AgentHQDemo.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class SegmentsController(RetailAnalyticsService service) : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<List<CustomerSegment>>> GetAll()
    {
        return Ok(await service.GetSegmentsAsync());
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<CustomerSegment>> Get(int id)
    {
        var segment = await service.GetSegmentAsync(id);
        if (segment == null) return NotFound();
        return Ok(segment);
    }

    [HttpGet("predict/{customerId}")]
    public async Task<ActionResult<SegmentPrediction>> Predict(string customerId)
    {
        var prediction = await service.PredictSegmentAsync(customerId);
        return Ok(prediction);
    }
}
