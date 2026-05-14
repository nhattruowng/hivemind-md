package com.bizflow.workflow.exception;

public class RollbackFailedException extends RuntimeException {
    public RollbackFailedException(String message) {
        super(message);
    }
}
