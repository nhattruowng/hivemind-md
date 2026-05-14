package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflow_run_context")
public class WorkflowRunContext {
    @Id
    private String id;
    private String runId;
    private String contextKey;
    @Column(columnDefinition = "TEXT")
    private String valueJson;
    @Column(columnDefinition = "TEXT")
    private String redactedValueJson;
    private String createdAt;
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }
    public String getContextKey() { return contextKey; }
    public void setContextKey(String contextKey) { this.contextKey = contextKey; }
    public String getValueJson() { return valueJson; }
    public void setValueJson(String valueJson) { this.valueJson = valueJson; }
    public String getRedactedValueJson() { return redactedValueJson; }
    public void setRedactedValueJson(String redactedValueJson) { this.redactedValueJson = redactedValueJson; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
