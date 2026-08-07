namespace AgentHQDemo.Api.Models;

/// <summary>
/// Prediction result for customer segment classification.
/// </summary>
public record SegmentPrediction(
    string CustomerId,
    string PredictedSegment,
    double Confidence,
    string[] TopFeatures
);
