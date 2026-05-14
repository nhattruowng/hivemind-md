package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.NotBlank;

public record EventBindingRequest(
        @NotBlank String eventType,
        JsonNode condition,
        JsonNode sourceScope
) {
}
