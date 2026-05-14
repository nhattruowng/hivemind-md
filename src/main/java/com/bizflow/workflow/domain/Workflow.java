package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflows")
public class Workflow {
    @Id
    private String id;
    private String name;
    @Column(columnDefinition = "TEXT")
    private String description;
    @Enumerated(EnumType.STRING)
    private WorkflowStatus status;
    @Enumerated(EnumType.STRING)
    private WorkflowTriggerType triggerType;
    private int currentVersion;
    @Column(columnDefinition = "TEXT")
    private String definitionJson;
    @Column(columnDefinition = "TEXT")
    private String inputSchemaJson;
    @Column(columnDefinition = "TEXT")
    private String outputSchemaJson;
    @Column(columnDefinition = "TEXT")
    private String variablesJson;
    @Column(columnDefinition = "TEXT")
    private String errorPolicyJson;
    @Column(columnDefinition = "TEXT")
    private String approvalPolicyJson;
    @Column(columnDefinition = "TEXT")
    private String retryPolicyJson;
    @Column(columnDefinition = "TEXT")
    private String timeoutPolicyJson;
    private String createdBy;
    private String createdAt;
    private String updatedAt;
    private String deletedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public WorkflowStatus getStatus() { return status; }
    public void setStatus(WorkflowStatus status) { this.status = status; }
    public WorkflowTriggerType getTriggerType() { return triggerType; }
    public void setTriggerType(WorkflowTriggerType triggerType) { this.triggerType = triggerType; }
    public int getCurrentVersion() { return currentVersion; }
    public void setCurrentVersion(int currentVersion) { this.currentVersion = currentVersion; }
    public String getDefinitionJson() { return definitionJson; }
    public void setDefinitionJson(String definitionJson) { this.definitionJson = definitionJson; }
    public String getInputSchemaJson() { return inputSchemaJson; }
    public void setInputSchemaJson(String inputSchemaJson) { this.inputSchemaJson = inputSchemaJson; }
    public String getOutputSchemaJson() { return outputSchemaJson; }
    public void setOutputSchemaJson(String outputSchemaJson) { this.outputSchemaJson = outputSchemaJson; }
    public String getVariablesJson() { return variablesJson; }
    public void setVariablesJson(String variablesJson) { this.variablesJson = variablesJson; }
    public String getErrorPolicyJson() { return errorPolicyJson; }
    public void setErrorPolicyJson(String errorPolicyJson) { this.errorPolicyJson = errorPolicyJson; }
    public String getApprovalPolicyJson() { return approvalPolicyJson; }
    public void setApprovalPolicyJson(String approvalPolicyJson) { this.approvalPolicyJson = approvalPolicyJson; }
    public String getRetryPolicyJson() { return retryPolicyJson; }
    public void setRetryPolicyJson(String retryPolicyJson) { this.retryPolicyJson = retryPolicyJson; }
    public String getTimeoutPolicyJson() { return timeoutPolicyJson; }
    public void setTimeoutPolicyJson(String timeoutPolicyJson) { this.timeoutPolicyJson = timeoutPolicyJson; }
    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    public String getDeletedAt() { return deletedAt; }
    public void setDeletedAt(String deletedAt) { this.deletedAt = deletedAt; }
}
