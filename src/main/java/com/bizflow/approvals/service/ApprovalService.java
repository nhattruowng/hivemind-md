package com.bizflow.approvals.service;

import com.bizflow.approvals.domain.ApprovalRequest;
import com.bizflow.approvals.repository.ApprovalRequestRepository;
import com.bizflow.common.domain.ApprovalStatus;
import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.util.Ids;
import com.bizflow.workflow.dto.ApprovalDecisionRequest;
import com.bizflow.workflow.service.WorkflowAuditService;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ApprovalService {
    private final ApprovalRequestRepository repository;
    private final ObjectMapper objectMapper;
    private final WorkflowAuditService auditService;

    public ApprovalService(ApprovalRequestRepository repository, ObjectMapper objectMapper, WorkflowAuditService auditService) {
        this.repository = repository;
        this.objectMapper = objectMapper;
        this.auditService = auditService;
    }

    @Transactional
    public ApprovalRequest createApprovalRequest(String workflowId, String runId, String stepRunId, String stepName,
                                                 String actionType, String toolName, RiskLevel riskLevel,
                                                 PermissionLevel permissionLevel, Object action, Object diffPreview) {
        ApprovalRequest approval = new ApprovalRequest();
        approval.setId(Ids.newId("apr"));
        approval.setWorkflowId(workflowId);
        approval.setRunId(runId);
        approval.setStepRunId(stepRunId);
        approval.setStepName(stepName);
        approval.setToolName(toolName);
        approval.setActionType(actionType);
        approval.setResourceType("workflow_step");
        approval.setResourceId(stepRunId);
        approval.setRiskLevel(riskLevel);
        approval.setPermissionLevel(permissionLevel.name());
        approval.setStatus(ApprovalStatus.PENDING);
        approval.setRequestedBy("workflow_engine");
        approval.setPreviewJson(write(action));
        approval.setInputPreviewJson(write(action));
        approval.setOutputPreviewJson("{}");
        approval.setExpectedEffect("Execute workflow step: " + stepName);
        approval.setDiffPreviewJson(write(diffPreview));
        approval.setActionJson(write(action));
        approval.setCreatedAt(Instant.now().toString());
        ApprovalRequest saved = repository.save(approval);
        auditService.logEvent(workflowId, runId, stepRunId, "approval_requested", "pending",
                "Approval requested for step " + stepName, riskLevel, saved);
        return saved;
    }

    public List<ApprovalRequest> listPending() {
        return repository.findByStatusOrderByCreatedAtDesc(ApprovalStatus.PENDING);
    }

    public ApprovalRequest get(String approvalId) {
        return repository.findById(approvalId)
                .orElseThrow(() -> new IllegalArgumentException("Approval not found: " + approvalId));
    }

    @Transactional
    public ApprovalRequest approve(String approvalId, ApprovalDecisionRequest request) {
        ApprovalRequest approval = get(approvalId);
        approval.setStatus(ApprovalStatus.APPROVED);
        approval.setDecisionJson(write(request));
        approval.setReason(request == null ? null : request.reason());
        approval.setDecidedAt(Instant.now().toString());
        ApprovalRequest saved = repository.save(approval);
        auditService.logEvent(approval.getWorkflowId(), approval.getRunId(), approval.getStepRunId(),
                "approval_decided", "approved", "Approval approved", approval.getRiskLevel(), saved);
        return saved;
    }

    @Transactional
    public ApprovalRequest reject(String approvalId, ApprovalDecisionRequest request) {
        ApprovalRequest approval = get(approvalId);
        approval.setStatus(ApprovalStatus.REJECTED);
        approval.setDecisionJson(write(request));
        approval.setReason(request == null ? null : request.reason());
        approval.setDecidedAt(Instant.now().toString());
        ApprovalRequest saved = repository.save(approval);
        auditService.logEvent(approval.getWorkflowId(), approval.getRunId(), approval.getStepRunId(),
                "approval_decided", "rejected", "Approval rejected", approval.getRiskLevel(), saved);
        return saved;
    }

    @Transactional
    public ApprovalRequest modifyAndApprove(String approvalId, ApprovalDecisionRequest request) {
        ApprovalRequest approval = get(approvalId);
        approval.setStatus(ApprovalStatus.MODIFIED);
        approval.setActionJson(write(request == null ? null : request.modifiedAction()));
        approval.setDecisionJson(write(request));
        approval.setReason(request == null ? null : request.reason());
        approval.setDecidedAt(Instant.now().toString());
        ApprovalRequest saved = repository.save(approval);
        auditService.logEvent(approval.getWorkflowId(), approval.getRunId(), approval.getStepRunId(),
                "approval_decided", "modified", "Approval modified and approved", approval.getRiskLevel(), saved);
        return saved;
    }

    private String write(Object value) {
        try {
            return objectMapper.writeValueAsString(value == null ? "{}" : value);
        } catch (Exception e) {
            return "{}";
        }
    }
}
