package com.bizflow.workflow.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Getter
@Setter
@NoArgsConstructor
@Accessors(chain = true)
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
}
