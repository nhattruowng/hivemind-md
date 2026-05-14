package com.bizflow.workflow.exception;

public class ApprovalRequiredException extends RuntimeException {
    private final String approvalRequestId;

    public ApprovalRequiredException(String approvalRequestId, String message) {
        super(message);
        this.approvalRequestId = approvalRequestId;
    }

    public String getApprovalRequestId() {
        return approvalRequestId;
    }
}
