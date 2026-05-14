package com.bizflow.workflow.exception;

public class WorkflowPausedException extends RuntimeException {
    public WorkflowPausedException(String message) {
        super(message);
    }
}
