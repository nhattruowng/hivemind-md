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
@Table(name = "workflow_variables")
public class WorkflowVariable {
    @Id
    private String id;
    private String workflowId;
    private String name;
    @Column(columnDefinition = "TEXT")
    private String valueJson;
    @Column(name = "is_secret")
    private boolean secret;
    private String createdAt;
    private String updatedAt;
}
