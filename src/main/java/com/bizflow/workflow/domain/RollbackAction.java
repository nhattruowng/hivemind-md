package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "rollback_actions")
public class RollbackAction {
    @Id
    private String id;
    private String workflowId;
    private String stepKey;
    private String compensationType;
    @Column(columnDefinition = "TEXT")
    private String compensationJson;
    private boolean requiresApproval;
    private String status;
    private String createdAt;
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public String getStepKey() { return stepKey; }
    public void setStepKey(String stepKey) { this.stepKey = stepKey; }
    public String getCompensationType() { return compensationType; }
    public void setCompensationType(String compensationType) { this.compensationType = compensationType; }
    public String getCompensationJson() { return compensationJson; }
    public void setCompensationJson(String compensationJson) { this.compensationJson = compensationJson; }
    public boolean isRequiresApproval() { return requiresApproval; }
    public void setRequiresApproval(boolean requiresApproval) { this.requiresApproval = requiresApproval; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
