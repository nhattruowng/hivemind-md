package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflow_runs")
public class WorkflowRun {
    @Id
    private String id;
    private String workflowId;
    private int workflowVersion;
    @Enumerated(EnumType.STRING)
    private WorkflowRunStatus status;
    @Enumerated(EnumType.STRING)
    private WorkflowTriggerType triggerType;
    @Column(columnDefinition = "TEXT")
    private String inputJson;
    @Column(columnDefinition = "TEXT")
    private String outputJson;
    @Column(columnDefinition = "TEXT")
    private String errorJson;
    private String replayParentRunId;
    private String replayFromStepRunId;
    private String idempotencyKey;
    private String createdBy;
    private String startedAt;
    private String updatedAt;
    private String completedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public int getWorkflowVersion() { return workflowVersion; }
    public void setWorkflowVersion(int workflowVersion) { this.workflowVersion = workflowVersion; }
    public WorkflowRunStatus getStatus() { return status; }
    public void setStatus(WorkflowRunStatus status) { this.status = status; }
    public WorkflowTriggerType getTriggerType() { return triggerType; }
    public void setTriggerType(WorkflowTriggerType triggerType) { this.triggerType = triggerType; }
    public String getInputJson() { return inputJson; }
    public void setInputJson(String inputJson) { this.inputJson = inputJson; }
    public String getOutputJson() { return outputJson; }
    public void setOutputJson(String outputJson) { this.outputJson = outputJson; }
    public String getErrorJson() { return errorJson; }
    public void setErrorJson(String errorJson) { this.errorJson = errorJson; }
    public String getReplayParentRunId() { return replayParentRunId; }
    public void setReplayParentRunId(String replayParentRunId) { this.replayParentRunId = replayParentRunId; }
    public String getReplayFromStepRunId() { return replayFromStepRunId; }
    public void setReplayFromStepRunId(String replayFromStepRunId) { this.replayFromStepRunId = replayFromStepRunId; }
    public String getIdempotencyKey() { return idempotencyKey; }
    public void setIdempotencyKey(String idempotencyKey) { this.idempotencyKey = idempotencyKey; }
    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
    public String getStartedAt() { return startedAt; }
    public void setStartedAt(String startedAt) { this.startedAt = startedAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
}
