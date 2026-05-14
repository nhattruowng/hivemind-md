package com.bizflow.workflow.exception;

public class RetryExhaustedException extends RuntimeException {
    public RetryExhaustedException(String message) {
        super(message);
    }
}
