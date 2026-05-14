package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "workflow_replay_runs")
public class WorkflowReplayRun {
    @Id
    private String id;
    private String parentRunId;
    private String replayRunId;
    private String fromStepRunId;
    @Column(columnDefinition = "TEXT")
    private String inputOverrideJson;
    private String createdBy;
    private String createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getParentRunId() { return parentRunId; }
    public void setParentRunId(String parentRunId) { this.parentRunId = parentRunId; }
    public String getReplayRunId() { return replayRunId; }
    public void setReplayRunId(String replayRunId) { this.replayRunId = replayRunId; }
    public String getFromStepRunId() { return fromStepRunId; }
    public void setFromStepRunId(String fromStepRunId) { this.fromStepRunId = fromStepRunId; }
    public String getInputOverrideJson() { return inputOverrideJson; }
    public void setInputOverrideJson(String inputOverrideJson) { this.inputOverrideJson = inputOverrideJson; }
    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
