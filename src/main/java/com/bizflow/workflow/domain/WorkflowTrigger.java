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
@Table(name = "workflow_triggers")
public class WorkflowTrigger {
    @Id
    private String id;
    private String workflowId;
    @Enumerated(EnumType.STRING)
    private WorkflowTriggerType triggerType;
    @Column(columnDefinition = "TEXT")
    private String configJson;
    private boolean enabled;
    private String createdAt;
    private String updatedAt;
}
