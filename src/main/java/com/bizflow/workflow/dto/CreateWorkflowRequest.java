package com.bizflow.workflow.dto;

import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record CreateWorkflowRequest(
        @NotBlank String name,
        String description,
        @NotNull WorkflowTriggerType triggerType,
        @NotNull JsonNode definition,
        String createdBy
) {
}
