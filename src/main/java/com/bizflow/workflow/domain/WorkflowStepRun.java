package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflow_step_runs")
public class WorkflowStepRun {
    @Id
    private String id;
    private String runId;
    private String workflowId;
    private String stepKey;
    private String stepName;
    @Enumerated(EnumType.STRING)
    private WorkflowStepType stepType;
    @Enumerated(EnumType.STRING)
    private WorkflowStepRunStatus status;
    private int attempt;
    private int maxAttempts;
    @Column(columnDefinition = "TEXT")
    private String inputJson;
    @Column(columnDefinition = "TEXT")
    private String outputJson;
    @Column(columnDefinition = "TEXT")
    private String redactedInputJson;
    @Column(columnDefinition = "TEXT")
    private String redactedOutputJson;
    @Column(columnDefinition = "TEXT")
    private String errorJson;
    private String approvalRequestId;
    private String toolCallLogId;
    private String modelCallLogId;
    private String startedAt;
    private String updatedAt;
    private String completedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public String getStepKey() { return stepKey; }
    public void setStepKey(String stepKey) { this.stepKey = stepKey; }
    public String getStepName() { return stepName; }
    public void setStepName(String stepName) { this.stepName = stepName; }
    public WorkflowStepType getStepType() { return stepType; }
    public void setStepType(WorkflowStepType stepType) { this.stepType = stepType; }
    public WorkflowStepRunStatus getStatus() { return status; }
    public void setStatus(WorkflowStepRunStatus status) { this.status = status; }
    public int getAttempt() { return attempt; }
    public void setAttempt(int attempt) { this.attempt = attempt; }
    public int getMaxAttempts() { return maxAttempts; }
    public void setMaxAttempts(int maxAttempts) { this.maxAttempts = maxAttempts; }
    public String getInputJson() { return inputJson; }
    public void setInputJson(String inputJson) { this.inputJson = inputJson; }
    public String getOutputJson() { return outputJson; }
    public void setOutputJson(String outputJson) { this.outputJson = outputJson; }
    public String getRedactedInputJson() { return redactedInputJson; }
    public void setRedactedInputJson(String redactedInputJson) { this.redactedInputJson = redactedInputJson; }
    public String getRedactedOutputJson() { return redactedOutputJson; }
    public void setRedactedOutputJson(String redactedOutputJson) { this.redactedOutputJson = redactedOutputJson; }
    public String getErrorJson() { return errorJson; }
    public void setErrorJson(String errorJson) { this.errorJson = errorJson; }
    public String getApprovalRequestId() { return approvalRequestId; }
    public void setApprovalRequestId(String approvalRequestId) { this.approvalRequestId = approvalRequestId; }
    public String getToolCallLogId() { return toolCallLogId; }
    public void setToolCallLogId(String toolCallLogId) { this.toolCallLogId = toolCallLogId; }
    public String getModelCallLogId() { return modelCallLogId; }
    public void setModelCallLogId(String modelCallLogId) { this.modelCallLogId = modelCallLogId; }
    public String getStartedAt() { return startedAt; }
    public void setStartedAt(String startedAt) { this.startedAt = startedAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
}
