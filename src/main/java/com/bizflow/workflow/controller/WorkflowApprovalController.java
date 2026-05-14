package com.bizflow.workflow.controller;

import com.bizflow.approvals.domain.ApprovalRequest;
import com.bizflow.approvals.service.ApprovalService;
import com.bizflow.common.reactive.BlockingJpaBridge;
import com.bizflow.workflow.dto.ApprovalDecisionRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/approvals")
@RequiredArgsConstructor
public class WorkflowApprovalController {
    private final ApprovalService approvalService;
    private final BlockingJpaBridge blockingJpa;

    @GetMapping
    public Flux<ApprovalRequest> listPending() {
        return blockingJpa.flux(approvalService::listPending);
    }

    @GetMapping("/{approvalId}")
    public Mono<ApprovalRequest> get(@PathVariable String approvalId) {
        return blockingJpa.mono(() -> approvalService.get(approvalId));
    }

    @PostMapping("/{approvalId}/approve")
    public Mono<ApprovalRequest> approve(
            @PathVariable String approvalId,
            @RequestBody(required = false) ApprovalDecisionRequest request
    ) {
        return blockingJpa.mono(() -> approvalService.approve(approvalId, request));
    }

    @PostMapping("/{approvalId}/reject")
    public Mono<ApprovalRequest> reject(
            @PathVariable String approvalId,
            @RequestBody(required = false) ApprovalDecisionRequest request
    ) {
        return blockingJpa.mono(() -> approvalService.reject(approvalId, request));
    }

    @PostMapping("/{approvalId}/modify-and-approve")
    public Mono<ApprovalRequest> modifyAndApprove(
            @PathVariable String approvalId,
            @RequestBody ApprovalDecisionRequest request
    ) {
        return blockingJpa.mono(() -> approvalService.modifyAndApprove(approvalId, request));
    }
}
