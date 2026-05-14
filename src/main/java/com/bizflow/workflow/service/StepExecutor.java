package com.bizflow.workflow.service;

import com.bizflow.approvals.domain.ApprovalRequest;
import com.bizflow.approvals.service.ApprovalService;
import com.bizflow.common.domain.ApprovalStatus;
import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.WorkflowStep;
import com.bizflow.workflow.domain.WorkflowStepRun;
import com.bizflow.workflow.domain.WorkflowStepRunStatus;
import com.bizflow.workflow.domain.WorkflowStepType;
import com.bizflow.workflow.exception.ApprovalRequiredException;
import com.bizflow.workflow.exception.StepExecutionException;
import com.bizflow.workflow.repository.WorkflowStepRunRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class StepExecutor {
    private final WorkflowStepRunRepository stepRunRepository;
    private final ApprovalService approvalService;
    private final WorkflowAuditService auditService;
    private final ObjectMapper objectMapper;

    public StepExecutor(WorkflowStepRunRepository stepRunRepository, ApprovalService approvalService,
                        WorkflowAuditService auditService, ObjectMapper objectMapper) {
        this.stepRunRepository = stepRunRepository;
        this.approvalService = approvalService;
        this.auditService = auditService;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public WorkflowStepRun executeStep(String runId, WorkflowStep step, String workflowId) {
        WorkflowStepRun stepRun = createStepRun(runId, step, workflowId);
        auditService.logEvent(workflowId, runId, stepRun.getId(), "step_started", "running",
                "Started step " + step.getName(), step.getRiskLevel(), step);
        try {
            if (requiresApproval(step)) {
                ApprovalRequest approval = approvalService.createApprovalRequest(
                        workflowId,
                        runId,
                        stepRun.getId(),
                        step.getName(),
                        step.getType().name().toLowerCase(),
                        toolName(step),
                        step.getRiskLevel(),
                        step.getPermissionLevel(),
                        Map.of("step_key", step.getStepKey(), "input", step.getInputJson()),
                        Map.of()
                );
                stepRun.setApprovalRequestId(approval.getId());
                stepRun.setStatus(WorkflowStepRunStatus.WAITING_APPROVAL);
                stepRun.setUpdatedAt(Instant.now().toString());
                stepRunRepository.save(stepRun);
                throw new ApprovalRequiredException(approval.getId(), "Workflow step requires approval");
            }

            String output = switch (step.getType()) {
                case TOOL_CALL -> executeToolCallStep(step);
                case AGENT_TASK -> executeAgentTaskStep(step);
                case CONDITION -> executeConditionStep(step);
                case LOOP -> executeLoopStep(step);
                case APPROVAL -> executeApprovalStep(step);
                case DELAY -> executeDelayStep(step);
                case NOTIFICATION -> executeNotificationStep(step);
                case TRANSFORM -> executeTransformStep(step);
                case MEMORY_SEARCH -> executeMemorySearchStep(step);
                case MODEL_CALL -> executeModelCallStep(step);
                case SUB_WORKFLOW -> executeSubWorkflowStep(step);
            };
            stepRun.setOutputJson(output);
            stepRun.setRedactedOutputJson(auditService.redact(output));
            stepRun.setStatus(WorkflowStepRunStatus.SUCCESS);
            stepRun.setCompletedAt(Instant.now().toString());
            stepRun.setUpdatedAt(stepRun.getCompletedAt());
            WorkflowStepRun saved = stepRunRepository.save(stepRun);
            auditService.logEvent(workflowId, runId, saved.getId(), "step_succeeded", "success",
                    "Completed step " + step.getName(), step.getRiskLevel(), output);
            return saved;
        } catch (ApprovalRequiredException e) {
            throw e;
        } catch (Exception e) {
            stepRun.setStatus(WorkflowStepRunStatus.FAILED);
            stepRun.setErrorJson(write(Map.of("message", e.getMessage())));
            stepRun.setCompletedAt(Instant.now().toString());
            stepRun.setUpdatedAt(stepRun.getCompletedAt());
            stepRunRepository.save(stepRun);
            auditService.logEvent(workflowId, runId, stepRun.getId(), "step_failed", "failed",
                    "Failed step " + step.getName(), step.getRiskLevel(), stepRun.getErrorJson());
            throw new StepExecutionException("Step failed: " + step.getName(), e);
        }
    }

    public String executeToolCallStep(WorkflowStep step) {
        return write(Map.of("type", "tool_call", "status", "stubbed", "input", step.getInputJson()));
    }

    public String executeAgentTaskStep(WorkflowStep step) {
        return write(Map.of("type", "agent_task", "status", "stubbed"));
    }

    public String executeConditionStep(WorkflowStep step) {
        return write(Map.of("condition_result", true));
    }

    public String executeLoopStep(WorkflowStep step) {
        return write(Map.of("loop_iterations", 0, "status", "stubbed"));
    }

    public String executeApprovalStep(WorkflowStep step) {
        return write(Map.of("approval_step", "passed"));
    }

    public String executeDelayStep(WorkflowStep step) {
        return write(Map.of("delayed", true));
    }

    public String executeNotificationStep(WorkflowStep step) {
        return write(Map.of("notified", true));
    }

    public String executeTransformStep(WorkflowStep step) {
        return write(Map.of("transformed", true, "input", step.getInputJson()));
    }

    public String executeMemorySearchStep(WorkflowStep step) {
        return write(Map.of("results", new Object[0], "status", "stubbed"));
    }

    public String executeModelCallStep(WorkflowStep step) {
        return write(Map.of("model_response", "stubbed"));
    }

    public String executeSubWorkflowStep(WorkflowStep step) {
        return write(Map.of("sub_workflow_run", "stubbed"));
    }

    private WorkflowStepRun createStepRun(String runId, WorkflowStep step, String workflowId) {
        String now = Instant.now().toString();
        WorkflowStepRun stepRun = new WorkflowStepRun();
        stepRun.setId(Ids.newId("wsr"));
        stepRun.setRunId(runId);
        stepRun.setWorkflowId(workflowId);
        stepRun.setStepKey(step.getStepKey());
        stepRun.setStepName(step.getName());
        stepRun.setStepType(step.getType());
        stepRun.setStatus(WorkflowStepRunStatus.RUNNING);
        stepRun.setAttempt(1);
        stepRun.setMaxAttempts(1);
        stepRun.setInputJson(step.getInputJson());
        stepRun.setRedactedInputJson(auditService.redact(step.getInputJson()));
        stepRun.setStartedAt(now);
        stepRun.setUpdatedAt(now);
        return stepRunRepository.save(stepRun);
    }

    private boolean requiresApproval(WorkflowStep step) {
        if (step.isRequiresApproval()) {
            return true;
        }
        if (step.getRiskLevel() == RiskLevel.CRITICAL || step.getRiskLevel() == RiskLevel.HIGH) {
            return true;
        }
        if (step.getPermissionLevel() == PermissionLevel.EXECUTE_WITH_APPROVAL || step.getPermissionLevel() == PermissionLevel.FORBIDDEN) {
            return true;
        }
        if (step.getType() == WorkflowStepType.TOOL_CALL) {
            String lower = step.getInputJson() == null ? "" : step.getInputJson().toLowerCase();
            return lower.contains("write") || lower.contains("delete") || lower.contains("send_email")
                    || lower.contains("shell") || lower.contains("network");
        }
        return false;
    }

    private String toolName(WorkflowStep step) {
        try {
            return objectMapper.readTree(step.getInputJson()).path("tool_name").asText(null);
        } catch (Exception e) {
            return null;
        }
    }

    private String write(Object value) {
        try {
            return objectMapper.writeValueAsString(value);
        } catch (Exception e) {
            return "{}";
        }
    }
}
