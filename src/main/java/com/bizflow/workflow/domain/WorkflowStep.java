package com.bizflow.workflow.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
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
@Table(name = "workflow_steps")
public class WorkflowStep {
    @Id
    private String id;
    private String workflowId;
    private String stepKey;
    private String name;
    @Enumerated(EnumType.STRING)
    private WorkflowStepType type;
    @Column(columnDefinition = "TEXT")
    private String description;
    @Column(columnDefinition = "TEXT")
    private String inputJson;
    @Column(columnDefinition = "TEXT")
    private String outputMappingJson;
    @Column(columnDefinition = "TEXT")
    private String dependsOnJson;
    @Column(columnDefinition = "TEXT")
    private String conditionJson;
    @Column(columnDefinition = "TEXT")
    private String retryPolicyJson;
    private int timeoutMs;
    private boolean requiresApproval;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    @Enumerated(EnumType.STRING)
    private PermissionLevel permissionLevel;
    @Column(columnDefinition = "TEXT")
    private String compensationJson;
    @Column(columnDefinition = "TEXT")
    private String onSuccessJson;
    @Column(columnDefinition = "TEXT")
    private String onFailureJson;
    @Column(columnDefinition = "TEXT")
    private String metadataJson;
    private int stepOrder;
    private String createdAt;
    private String updatedAt;
}
