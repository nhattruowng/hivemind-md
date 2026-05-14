package com.bizflow.workflow.mapper;

import com.bizflow.workflow.domain.Workflow;
import com.bizflow.workflow.domain.WorkflowAuditEvent;
import com.bizflow.workflow.domain.WorkflowEventBinding;
import com.bizflow.workflow.domain.WorkflowRun;
import com.bizflow.workflow.domain.WorkflowSchedule;
import com.bizflow.workflow.domain.WorkflowStepRun;
import com.bizflow.workflow.domain.WorkflowVersion;
import com.bizflow.workflow.dto.EventBindingResponse;
import com.bizflow.workflow.dto.ScheduleResponse;
import com.bizflow.workflow.dto.WorkflowAuditEventResponse;
import com.bizflow.workflow.dto.WorkflowResponse;
import com.bizflow.workflow.dto.WorkflowRunResponse;
import com.bizflow.workflow.dto.WorkflowStepRunResponse;
import com.bizflow.workflow.dto.WorkflowVersionResponse;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class WorkflowMapper {
    private final ObjectMapper objectMapper;

    public WorkflowResponse toResponse(Workflow workflow) {
        return new WorkflowResponse(
                workflow.getId(),
                workflow.getName(),
                workflow.getDescription(),
                workflow.getStatus(),
                workflow.getTriggerType(),
                workflow.getCurrentVersion(),
                read(workflow.getDefinitionJson()),
                workflow.getCreatedBy(),
                workflow.getCreatedAt(),
                workflow.getUpdatedAt()
        );
    }

    public WorkflowVersionResponse toResponse(WorkflowVersion version) {
        return new WorkflowVersionResponse(
                version.getId(),
                version.getWorkflowId(),
                version.getVersion(),
                read(version.getDefinitionJson()),
                version.getChangeReason(),
                version.getCreatedBy(),
                version.getCreatedAt()
        );
    }

    public WorkflowRunResponse toResponse(WorkflowRun run) {
        return new WorkflowRunResponse(
                run.getId(),
                run.getWorkflowId(),
                run.getWorkflowVersion(),
                run.getStatus(),
                run.getTriggerType(),
                read(run.getInputJson()),
                read(run.getOutputJson()),
                read(run.getErrorJson()),
                run.getReplayParentRunId(),
                run.getCreatedBy(),
                run.getStartedAt(),
                run.getCompletedAt()
        );
    }

    public WorkflowStepRunResponse toResponse(WorkflowStepRun stepRun) {
        return new WorkflowStepRunResponse(
                stepRun.getId(),
                stepRun.getRunId(),
                stepRun.getStepKey(),
                stepRun.getStepName(),
                stepRun.getStepType(),
                stepRun.getStatus(),
                stepRun.getAttempt(),
                read(stepRun.getRedactedInputJson()),
                read(stepRun.getRedactedOutputJson()),
                read(stepRun.getErrorJson()),
                stepRun.getApprovalRequestId(),
                stepRun.getStartedAt(),
                stepRun.getCompletedAt()
        );
    }

    public WorkflowAuditEventResponse toResponse(WorkflowAuditEvent event) {
        return new WorkflowAuditEventResponse(
                event.getId(),
                event.getEventType(),
                event.getStatus(),
                event.getMessage(),
                read(event.getRedactedPayloadJson()),
                event.getCreatedAt()
        );
    }

    public ScheduleResponse toResponse(WorkflowSchedule schedule) {
        return new ScheduleResponse(
                schedule.getId(),
                schedule.getWorkflowId(),
                schedule.getCronExpression(),
                schedule.getTimezone(),
                schedule.getNextRunAt(),
                schedule.isEnabled()
        );
    }

    public EventBindingResponse toResponse(WorkflowEventBinding binding) {
        return new EventBindingResponse(
                binding.getId(),
                binding.getWorkflowId(),
                binding.getEventType(),
                read(binding.getConditionJson()),
                read(binding.getSourceScopeJson()),
                binding.isEnabled()
        );
    }

    private JsonNode read(String json) {
        try {
            if (json == null || json.isBlank()) {
                return objectMapper.createObjectNode();
            }
            return objectMapper.readTree(json);
        } catch (Exception e) {
            return objectMapper.createObjectNode();
        }
    }
}
