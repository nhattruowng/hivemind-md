package com.bizflow.workflow.domain;

import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflow_steps")
public class WorkflowStep {
    @Id
    private String id;
    private String workflowId;
    private String stepKey;
    private String name;
    @Enumerated(EnumType.STRING)
    private WorkflowStepType type;
    @Column(columnDefinition = "TEXT")
    private String description;
    @Column(columnDefinition = "TEXT")
    private String inputJson;
    @Column(columnDefinition = "TEXT")
    private String outputMappingJson;
    @Column(columnDefinition = "TEXT")
    private String dependsOnJson;
    @Column(columnDefinition = "TEXT")
    private String conditionJson;
    @Column(columnDefinition = "TEXT")
    private String retryPolicyJson;
    private int timeoutMs;
    private boolean requiresApproval;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    @Enumerated(EnumType.STRING)
    private PermissionLevel permissionLevel;
    @Column(columnDefinition = "TEXT")
    private String compensationJson;
    @Column(columnDefinition = "TEXT")
    private String onSuccessJson;
    @Column(columnDefinition = "TEXT")
    private String onFailureJson;
    @Column(columnDefinition = "TEXT")
    private String metadataJson;
    private int stepOrder;
    private String createdAt;
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public String getStepKey() { return stepKey; }
    public void setStepKey(String stepKey) { this.stepKey = stepKey; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public WorkflowStepType getType() { return type; }
    public void setType(WorkflowStepType type) { this.type = type; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getInputJson() { return inputJson; }
    public void setInputJson(String inputJson) { this.inputJson = inputJson; }
    public String getOutputMappingJson() { return outputMappingJson; }
    public void setOutputMappingJson(String outputMappingJson) { this.outputMappingJson = outputMappingJson; }
    public String getDependsOnJson() { return dependsOnJson; }
    public void setDependsOnJson(String dependsOnJson) { this.dependsOnJson = dependsOnJson; }
    public String getConditionJson() { return conditionJson; }
    public void setConditionJson(String conditionJson) { this.conditionJson = conditionJson; }
    public String getRetryPolicyJson() { return retryPolicyJson; }
    public void setRetryPolicyJson(String retryPolicyJson) { this.retryPolicyJson = retryPolicyJson; }
    public int getTimeoutMs() { return timeoutMs; }
    public void setTimeoutMs(int timeoutMs) { this.timeoutMs = timeoutMs; }
    public boolean isRequiresApproval() { return requiresApproval; }
    public void setRequiresApproval(boolean requiresApproval) { this.requiresApproval = requiresApproval; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }
    public PermissionLevel getPermissionLevel() { return permissionLevel; }
    public void setPermissionLevel(PermissionLevel permissionLevel) { this.permissionLevel = permissionLevel; }
    public String getCompensationJson() { return compensationJson; }
    public void setCompensationJson(String compensationJson) { this.compensationJson = compensationJson; }
    public String getOnSuccessJson() { return onSuccessJson; }
    public void setOnSuccessJson(String onSuccessJson) { this.onSuccessJson = onSuccessJson; }
    public String getOnFailureJson() { return onFailureJson; }
    public void setOnFailureJson(String onFailureJson) { this.onFailureJson = onFailureJson; }
    public String getMetadataJson() { return metadataJson; }
    public void setMetadataJson(String metadataJson) { this.metadataJson = metadataJson; }
    public int getStepOrder() { return stepOrder; }
    public void setStepOrder(int stepOrder) { this.stepOrder = stepOrder; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
