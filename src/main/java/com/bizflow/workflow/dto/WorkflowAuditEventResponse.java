package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record WorkflowAuditEventResponse(
        String id,
        String eventType,
        String status,
        String message,
        JsonNode payload,
        String createdAt
) {
}
