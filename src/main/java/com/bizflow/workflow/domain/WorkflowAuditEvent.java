package com.bizflow.workflow.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

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
@Table(name = "workflow_audit_events")
public class WorkflowAuditEvent {
    @Id
    private String id;
    private String workflowId;
    private String runId;
    private String stepRunId;
    private String eventType;
    private String status;
    @Column(columnDefinition = "TEXT")
    private String message;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    @Column(columnDefinition = "TEXT")
    private String redactedPayloadJson;
    private String createdAt;
}
