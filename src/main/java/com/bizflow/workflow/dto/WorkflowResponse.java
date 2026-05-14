package com.bizflow.workflow.dto;

import com.bizflow.workflow.domain.WorkflowStatus;
import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.fasterxml.jackson.databind.JsonNode;

public record WorkflowResponse(
        String id,
        String name,
        String description,
        WorkflowStatus status,
        WorkflowTriggerType triggerType,
        int version,
        JsonNode definition,
        String createdBy,
        String createdAt,
        String updatedAt
) {
}
