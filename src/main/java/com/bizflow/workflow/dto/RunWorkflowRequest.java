package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record RunWorkflowRequest(
        JsonNode input,
        String createdBy,
        String idempotencyKey
) {
}
