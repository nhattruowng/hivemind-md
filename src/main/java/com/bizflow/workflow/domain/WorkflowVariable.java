package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflow_variables")
public class WorkflowVariable {
    @Id
    private String id;
    private String workflowId;
    private String name;
    @Column(columnDefinition = "TEXT")
    private String valueJson;
    @Column(name = "is_secret")
    private boolean secret;
    private String createdAt;
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getValueJson() { return valueJson; }
    public void setValueJson(String valueJson) { this.valueJson = valueJson; }
    public boolean isSecret() { return secret; }
    public void setSecret(boolean secret) { this.secret = secret; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
