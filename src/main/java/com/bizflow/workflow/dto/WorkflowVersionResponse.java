package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record WorkflowVersionResponse(
        String id,
        String workflowId,
        int version,
        JsonNode definition,
        String changeReason,
        String createdBy,
        String createdAt
) {
}
