package com.bizflow.workflow.service;

import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.WorkflowAuditEvent;
import com.bizflow.workflow.repository.WorkflowAuditEventRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class WorkflowAuditService {
    private final WorkflowAuditEventRepository repository;
    private final ObjectMapper objectMapper;

    public WorkflowAuditService(WorkflowAuditEventRepository repository, ObjectMapper objectMapper) {
        this.repository = repository;
        this.objectMapper = objectMapper;
    }

    public WorkflowAuditEvent logEvent(String workflowId, String runId, String stepRunId, String eventType,
                                       String status, String message, RiskLevel riskLevel, Object payload) {
        WorkflowAuditEvent event = new WorkflowAuditEvent();
        event.setId(Ids.newId("waud"));
        event.setWorkflowId(workflowId);
        event.setRunId(runId);
        event.setStepRunId(stepRunId);
        event.setEventType(eventType);
        event.setStatus(status);
        event.setMessage(message);
        event.setRiskLevel(riskLevel);
        event.setRedactedPayloadJson(redact(payload));
        event.setCreatedAt(Instant.now().toString());
        return repository.save(event);
    }

    public List<WorkflowAuditEvent> getTimeline(String runId) {
        return repository.findByRunIdOrderByCreatedAtAsc(runId);
    }

    public String redact(Object payload) {
        try {
            String json = objectMapper.writeValueAsString(payload == null ? "{}" : payload);
            return json
                    .replaceAll("(?i)(api[_-]?key|token|password|secret)\"\\s*:\\s*\"[^\"]+\"", "$1\":\"[REDACTED_SECRET]\"")
                    .replaceAll("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", "[REDACTED_EMAIL]");
        } catch (Exception e) {
            return "{}";
        }
    }
}
