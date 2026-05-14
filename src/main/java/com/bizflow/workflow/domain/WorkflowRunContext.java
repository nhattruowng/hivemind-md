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
}
