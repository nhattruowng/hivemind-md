package com.bizflow.workflow.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record ReplayStepRequest(
        JsonNode inputOverride,
        String createdBy
) {
}
