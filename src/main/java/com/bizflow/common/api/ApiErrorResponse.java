package com.bizflow.common.api;

import java.time.Instant;
import java.util.Map;

public record ApiErrorResponse(
        String code,
        String message,
        Map<String, Object> details,
        String timestamp
) {
    public static ApiErrorResponse of(String code, String message, Map<String, Object> details) {
        return new ApiErrorResponse(code, message, details, Instant.now().toString());
    }
}
