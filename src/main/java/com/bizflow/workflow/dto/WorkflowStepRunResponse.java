package com.bizflow.workflow.dto;

import com.bizflow.workflow.domain.WorkflowStepRunStatus;
import com.bizflow.workflow.domain.WorkflowStepType;
import com.fasterxml.jackson.databind.JsonNode;

public record WorkflowStepRunResponse(
        String id,
        String runId,
        String stepKey,
        String stepName,
        WorkflowStepType stepType,
        WorkflowStepRunStatus status,
        int attempt,
        JsonNode input,
        JsonNode output,
        JsonNode error,
        String approvalRequestId,
        String startedAt,
        String completedAt
) {
}
