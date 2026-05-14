package com.bizflow.workflow.exception;

public class WorkflowCancelledException extends RuntimeException {
    public WorkflowCancelledException(String message) {
        super(message);
    }
}
