package com.bizflow.workflow.dto;

import jakarta.validation.constraints.NotBlank;

public record ScheduleRequest(
        @NotBlank String cronExpression,
        @NotBlank String timezone
) {
}
