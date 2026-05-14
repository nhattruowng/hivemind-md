package com.bizflow.workflow.domain;

public enum WorkflowStepRunStatus {
    PENDING,
    RUNNING,
    WAITING_APPROVAL,
    SUCCESS,
    FAILED,
    SKIPPED,
    CANCELLED,
    RETRYING,
    ROLLED_BACK,
    ROLLBACK_FAILED
}
