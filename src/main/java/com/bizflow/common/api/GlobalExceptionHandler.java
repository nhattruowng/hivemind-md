package com.bizflow.common.api;

import com.bizflow.workflow.exception.ApprovalRequiredException;
import com.bizflow.workflow.exception.WorkflowValidationException;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(WorkflowValidationException.class)
    public ResponseEntity<ApiErrorResponse> workflowValidation(WorkflowValidationException ex) {
        return ResponseEntity.badRequest().body(ApiErrorResponse.of("WORKFLOW_VALIDATION_FAILED", ex.getMessage(), Map.of()));
    }

    @ExceptionHandler(ApprovalRequiredException.class)
    public ResponseEntity<ApiErrorResponse> approvalRequired(ApprovalRequiredException ex) {
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(ApiErrorResponse.of(
                "APPROVAL_REQUIRED",
                ex.getMessage(),
                Map.of("approval_request_id", ex.getApprovalRequestId())
        ));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiErrorResponse> validation(MethodArgumentNotValidException ex) {
        return ResponseEntity.badRequest().body(ApiErrorResponse.of("VALIDATION_FAILED", "Request validation failed", Map.of()));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiErrorResponse> badRequest(IllegalArgumentException ex) {
        return ResponseEntity.badRequest().body(ApiErrorResponse.of("BAD_REQUEST", ex.getMessage(), Map.of()));
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ApiErrorResponse> runtime(RuntimeException ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiErrorResponse.of("INTERNAL_ERROR", ex.getMessage(), Map.of()));
    }
}
