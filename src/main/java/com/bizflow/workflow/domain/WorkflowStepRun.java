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
}
