package com.bizflow.workflow.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Getter
@Setter
@NoArgsConstructor
@Accessors(chain = true)
@Entity
@Table(name = "workflow_schedules")
public class WorkflowSchedule {
    @Id
    private String id;
    private String workflowId;
    private String cronExpression;
    private String timezone;
    private String nextRunAt;
    private String lastRunAt;
    private boolean enabled;
    private String createdAt;
    private String updatedAt;
}
