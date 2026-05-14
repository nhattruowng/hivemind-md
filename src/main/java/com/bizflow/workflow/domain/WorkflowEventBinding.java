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
@Table(name = "workflow_event_bindings")
public class WorkflowEventBinding {
    @Id
    private String id;
    private String workflowId;
    private String eventType;
    @Column(columnDefinition = "TEXT")
    private String conditionJson;
    @Column(columnDefinition = "TEXT")
    private String sourceScopeJson;
    private boolean enabled;
    private String createdAt;
    private String updatedAt;
}
