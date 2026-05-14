package com.bizflow.agent_runtime.domain;

import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.domain.RunStatus;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "agent_runs")
public class AgentRun {
    @Id
    private String id;
    private String userId;
    @Column(nullable = false, columnDefinition = "TEXT")
    private String userMessage;
    private String intent;
    @Enumerated(EnumType.STRING)
    private RunStatus status;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    private boolean requiresMemory;
    private boolean requiresTools;
    private boolean approvalRequired;
    private String approvalRequestId;
    private double confidence;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    private String createdAt;
    private String updatedAt;
    private String completedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    public String getUserMessage() { return userMessage; }
    public void setUserMessage(String userMessage) { this.userMessage = userMessage; }
    public String getIntent() { return intent; }
    public void setIntent(String intent) { this.intent = intent; }
    public RunStatus getStatus() { return status; }
    public void setStatus(RunStatus status) { this.status = status; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }
    public boolean isRequiresMemory() { return requiresMemory; }
    public void setRequiresMemory(boolean requiresMemory) { this.requiresMemory = requiresMemory; }
    public boolean isRequiresTools() { return requiresTools; }
    public void setRequiresTools(boolean requiresTools) { this.requiresTools = requiresTools; }
    public boolean isApprovalRequired() { return approvalRequired; }
    public void setApprovalRequired(boolean approvalRequired) { this.approvalRequired = approvalRequired; }
    public String getApprovalRequestId() { return approvalRequestId; }
    public void setApprovalRequestId(String approvalRequestId) { this.approvalRequestId = approvalRequestId; }
    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }
    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
}
