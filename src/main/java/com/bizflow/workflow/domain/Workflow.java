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
@Table(name = "workflows")
public class Workflow {
    @Id
    private String id;
    private String name;
    @Column(columnDefinition = "TEXT")
    private String description;
    @Enumerated(EnumType.STRING)
    private WorkflowStatus status;
    @Enumerated(EnumType.STRING)
    private WorkflowTriggerType triggerType;
    private int currentVersion;
    @Column(columnDefinition = "TEXT")
    private String definitionJson;
    @Column(columnDefinition = "TEXT")
    private String inputSchemaJson;
    @Column(columnDefinition = "TEXT")
    private String outputSchemaJson;
    @Column(columnDefinition = "TEXT")
    private String variablesJson;
    @Column(columnDefinition = "TEXT")
    private String errorPolicyJson;
    @Column(columnDefinition = "TEXT")
    private String approvalPolicyJson;
    @Column(columnDefinition = "TEXT")
    private String retryPolicyJson;
    @Column(columnDefinition = "TEXT")
    private String timeoutPolicyJson;
    private String createdBy;
    private String createdAt;
    private String updatedAt;
    private String deletedAt;
}
