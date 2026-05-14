package com.bizflow.workflow.domain;

public enum WorkflowErrorPolicy {
    FAIL_FAST,
    CONTINUE_ON_ERROR,
    RETRY_THEN_FAIL,
    SKIP_FAILED_STEP,
    REQUIRE_USER_DECISION
}
