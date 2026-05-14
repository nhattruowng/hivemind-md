package com.bizflow.workflow.dto;

import java.util.List;

public record WorkflowTimelineResponse(
        String runId,
        List<WorkflowAuditEventResponse> events,
        List<WorkflowStepRunResponse> steps
) {
}
