package com.bizflow.tools.domain;

import com.bizflow.common.domain.PermissionDecisionType;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.domain.ToolCallStatus;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "tool_call_logs")
public class ToolCallLog {
    @Id
    private String id;
    private String runId;
    private String toolName;
    @Enumerated(EnumType.STRING)
    private ToolCallStatus status;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    @Enumerated(EnumType.STRING)
    private PermissionDecisionType permissionDecision;
    @Column(columnDefinition = "TEXT")
    private String redactedInputJson;
    @Column(columnDefinition = "TEXT")
    private String redactedOutputJson;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    private String approvalRequestId;
    private String startedAt;
    private String completedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }
    public String getToolName() { return toolName; }
    public void setToolName(String toolName) { this.toolName = toolName; }
    public ToolCallStatus getStatus() { return status; }
    public void setStatus(ToolCallStatus status) { this.status = status; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }
    public PermissionDecisionType getPermissionDecision() { return permissionDecision; }
    public void setPermissionDecision(PermissionDecisionType permissionDecision) { this.permissionDecision = permissionDecision; }
    public String getRedactedInputJson() { return redactedInputJson; }
    public void setRedactedInputJson(String redactedInputJson) { this.redactedInputJson = redactedInputJson; }
    public String getRedactedOutputJson() { return redactedOutputJson; }
    public void setRedactedOutputJson(String redactedOutputJson) { this.redactedOutputJson = redactedOutputJson; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    public String getApprovalRequestId() { return approvalRequestId; }
    public void setApprovalRequestId(String approvalRequestId) { this.approvalRequestId = approvalRequestId; }
    public String getStartedAt() { return startedAt; }
    public void setStartedAt(String startedAt) { this.startedAt = startedAt; }
    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
}
