package com.bizflow.approvals.domain;

import com.bizflow.common.domain.ApprovalStatus;
import com.bizflow.common.domain.RiskLevel;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "approval_requests")
public class ApprovalRequest {
    @Id
    private String id;
    private String runId;
    private String workflowId;
    private String stepRunId;
    private String stepName;
    private String toolName;
    private String actionType;
    private String resourceType;
    private String resourceId;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    private String permissionLevel;
    @Enumerated(EnumType.STRING)
    private ApprovalStatus status;
    private String requestedBy;
    @Column(columnDefinition = "TEXT")
    private String previewJson;
    @Column(columnDefinition = "TEXT")
    private String inputPreviewJson;
    @Column(columnDefinition = "TEXT")
    private String outputPreviewJson;
    @Column(columnDefinition = "TEXT")
    private String expectedEffect;
    @Column(columnDefinition = "TEXT")
    private String diffPreviewJson;
    @Column(columnDefinition = "TEXT")
    private String actionJson;
    @Column(columnDefinition = "TEXT")
    private String decisionJson;
    @Column(columnDefinition = "TEXT")
    private String reason;
    private String createdAt;
    private String decidedAt;
    private String expiresAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public String getStepRunId() { return stepRunId; }
    public void setStepRunId(String stepRunId) { this.stepRunId = stepRunId; }
    public String getStepName() { return stepName; }
    public void setStepName(String stepName) { this.stepName = stepName; }
    public String getToolName() { return toolName; }
    public void setToolName(String toolName) { this.toolName = toolName; }
    public String getActionType() { return actionType; }
    public void setActionType(String actionType) { this.actionType = actionType; }
    public String getResourceType() { return resourceType; }
    public void setResourceType(String resourceType) { this.resourceType = resourceType; }
    public String getResourceId() { return resourceId; }
    public void setResourceId(String resourceId) { this.resourceId = resourceId; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }
    public String getPermissionLevel() { return permissionLevel; }
    public void setPermissionLevel(String permissionLevel) { this.permissionLevel = permissionLevel; }
    public ApprovalStatus getStatus() { return status; }
    public void setStatus(ApprovalStatus status) { this.status = status; }
    public String getRequestedBy() { return requestedBy; }
    public void setRequestedBy(String requestedBy) { this.requestedBy = requestedBy; }
    public String getPreviewJson() { return previewJson; }
    public void setPreviewJson(String previewJson) { this.previewJson = previewJson; }
    public String getInputPreviewJson() { return inputPreviewJson; }
    public void setInputPreviewJson(String inputPreviewJson) { this.inputPreviewJson = inputPreviewJson; }
    public String getOutputPreviewJson() { return outputPreviewJson; }
    public void setOutputPreviewJson(String outputPreviewJson) { this.outputPreviewJson = outputPreviewJson; }
    public String getExpectedEffect() { return expectedEffect; }
    public void setExpectedEffect(String expectedEffect) { this.expectedEffect = expectedEffect; }
    public String getDiffPreviewJson() { return diffPreviewJson; }
    public void setDiffPreviewJson(String diffPreviewJson) { this.diffPreviewJson = diffPreviewJson; }
    public String getActionJson() { return actionJson; }
    public void setActionJson(String actionJson) { this.actionJson = actionJson; }
    public String getDecisionJson() { return decisionJson; }
    public void setDecisionJson(String decisionJson) { this.decisionJson = decisionJson; }
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getDecidedAt() { return decidedAt; }
    public void setDecidedAt(String decidedAt) { this.decidedAt = decidedAt; }
    public String getExpiresAt() { return expiresAt; }
    public void setExpiresAt(String expiresAt) { this.expiresAt = expiresAt; }
}
