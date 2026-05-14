package com.bizflow.workflow.controller;

import com.bizflow.approvals.domain.ApprovalRequest;
import com.bizflow.approvals.service.ApprovalService;
import com.bizflow.workflow.dto.ApprovalDecisionRequest;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/approvals")
public class WorkflowApprovalController {
    private final ApprovalService approvalService;

    public WorkflowApprovalController(ApprovalService approvalService) {
        this.approvalService = approvalService;
    }

    @GetMapping
    public List<ApprovalRequest> listPending() {
        return approvalService.listPending();
    }

    @GetMapping("/{approvalId}")
    public ApprovalRequest get(@PathVariable String approvalId) {
        return approvalService.get(approvalId);
    }

    @PostMapping("/{approvalId}/approve")
    public ApprovalRequest approve(@PathVariable String approvalId, @RequestBody(required = false) ApprovalDecisionRequest request) {
        return approvalService.approve(approvalId, request);
    }

    @PostMapping("/{approvalId}/reject")
    public ApprovalRequest reject(@PathVariable String approvalId, @RequestBody(required = false) ApprovalDecisionRequest request) {
        return approvalService.reject(approvalId, request);
    }

    @PostMapping("/{approvalId}/modify-and-approve")
    public ApprovalRequest modifyAndApprove(@PathVariable String approvalId, @RequestBody ApprovalDecisionRequest request) {
        return approvalService.modifyAndApprove(approvalId, request);
    }
}
