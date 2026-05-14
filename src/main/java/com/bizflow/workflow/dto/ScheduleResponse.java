package com.bizflow.workflow.dto;

public record ScheduleResponse(
        String id,
        String workflowId,
        String cronExpression,
        String timezone,
        String nextRunAt,
        boolean enabled
) {
}
