package com.bizflow.workflow.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Getter
@Setter
@NoArgsConstructor
@Accessors(chain = true)
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
}
