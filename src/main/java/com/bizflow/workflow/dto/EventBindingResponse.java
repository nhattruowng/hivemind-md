package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record EventBindingResponse(
        String id,
        String workflowId,
        String eventType,
        JsonNode condition,
        JsonNode sourceScope,
        boolean enabled
) {
}
