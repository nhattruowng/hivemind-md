package com.bizflow.workflow.domain;

import com.bizflow.common.domain.RiskLevel;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

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

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getWorkflowId() { return workflowId; }
    public void setWorkflowId(String workflowId) { this.workflowId = workflowId; }
    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }
    public String getStepRunId() { return stepRunId; }
    public void setStepRunId(String stepRunId) { this.stepRunId = stepRunId; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }
    public String getRedactedPayloadJson() { return redactedPayloadJson; }
    public void setRedactedPayloadJson(String redactedPayloadJson) { this.redactedPayloadJson = redactedPayloadJson; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
