package com.bizflow.common.api;

import com.bizflow.workflow.exception.ApprovalRequiredException;
import com.bizflow.workflow.exception.WorkflowValidationException;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.support.WebExchangeBindException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import reactor.core.publisher.Mono;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(WorkflowValidationException.class)
    public Mono<ResponseEntity<ApiErrorResponse>> workflowValidation(WorkflowValidationException ex) {
        return error(HttpStatus.BAD_REQUEST, "WORKFLOW_VALIDATION_FAILED", ex.getMessage(), Map.of());
    }

    @ExceptionHandler(ApprovalRequiredException.class)
    public Mono<ResponseEntity<ApiErrorResponse>> approvalRequired(ApprovalRequiredException ex) {
        return error(
                HttpStatus.ACCEPTED,
                "APPROVAL_REQUIRED",
                ex.getMessage(),
                Map.of("approval_request_id", ex.getApprovalRequestId())
        );
    }

    @ExceptionHandler(WebExchangeBindException.class)
    public Mono<ResponseEntity<ApiErrorResponse>> validation(WebExchangeBindException ex) {
        return error(HttpStatus.BAD_REQUEST, "VALIDATION_FAILED", "Request validation failed", Map.of());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public Mono<ResponseEntity<ApiErrorResponse>> badRequest(IllegalArgumentException ex) {
        return error(HttpStatus.BAD_REQUEST, "BAD_REQUEST", ex.getMessage(), Map.of());
    }

    @ExceptionHandler(RuntimeException.class)
    public Mono<ResponseEntity<ApiErrorResponse>> runtime(RuntimeException ex) {
        log.error("Unhandled API exception", ex);
        return error(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", ex.getMessage(), Map.of());
    }

    private Mono<ResponseEntity<ApiErrorResponse>> error(
            HttpStatus status,
            String code,
            String message,
            Map<String, Object> details
    ) {
        return Mono.just(ResponseEntity.status(status).body(ApiErrorResponse.of(code, message, details)));
    }
}
