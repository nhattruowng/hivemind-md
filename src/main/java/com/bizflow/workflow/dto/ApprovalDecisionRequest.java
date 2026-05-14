package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record ApprovalDecisionRequest(
        String reason,
        JsonNode modifiedAction
) {
}
