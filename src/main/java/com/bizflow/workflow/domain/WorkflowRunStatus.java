package com.bizflow.workflow.domain;

public enum WorkflowRunStatus {
    PENDING,
    RUNNING,
    WAITING_APPROVAL,
    PAUSED,
    COMPLETED,
    FAILED,
    CANCELLED,
    ROLLBACK_RUNNING,
    ROLLBACK_COMPLETED,
    ROLLBACK_FAILED
}
