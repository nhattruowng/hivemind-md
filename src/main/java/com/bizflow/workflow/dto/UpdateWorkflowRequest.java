package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.NotNull;

public record UpdateWorkflowRequest(
        String name,
        String description,
        @NotNull JsonNode definition,
        String changeReason,
        String updatedBy
) {
}
