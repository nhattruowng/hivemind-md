package com.bizflow.workflow.dto;

import com.bizflow.workflow.domain.WorkflowRunStatus;
import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.fasterxml.jackson.databind.JsonNode;

public record WorkflowRunResponse(
        String id,
        String workflowId,
        int workflowVersion,
        WorkflowRunStatus status,
        WorkflowTriggerType triggerType,
        JsonNode input,
        JsonNode output,
        JsonNode error,
        String replayParentRunId,
        String createdBy,
        String startedAt,
        String completedAt
) {
}
