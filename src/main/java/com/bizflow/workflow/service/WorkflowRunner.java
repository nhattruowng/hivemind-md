package com.bizflow.workflow.service;

import com.bizflow.approvals.repository.ApprovalRequestRepository;
import com.bizflow.common.domain.ApprovalStatus;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.Workflow;
import com.bizflow.workflow.domain.WorkflowRun;
import com.bizflow.workflow.domain.WorkflowRunStatus;
import com.bizflow.workflow.domain.WorkflowStatus;
import com.bizflow.workflow.domain.WorkflowStep;
import com.bizflow.workflow.domain.WorkflowStepRun;
import com.bizflow.workflow.domain.WorkflowStepRunStatus;
import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.bizflow.workflow.dto.RunWorkflowRequest;
import com.bizflow.workflow.exception.ApprovalRequiredException;
import com.bizflow.workflow.exception.WorkflowCancelledException;
import com.bizflow.workflow.exception.WorkflowPausedException;
import com.bizflow.workflow.exception.WorkflowRunException;
import com.bizflow.workflow.repository.WorkflowRepository;
import com.bizflow.workflow.repository.WorkflowRunRepository;
import com.bizflow.workflow.repository.WorkflowStepRepository;
import com.bizflow.workflow.repository.WorkflowStepRunRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class WorkflowRunner {
    private final WorkflowRepository workflowRepository;
    private final WorkflowRunRepository runRepository;
    private final WorkflowStepRepository stepRepository;
    private final WorkflowStepRunRepository stepRunRepository;
    private final ApprovalRequestRepository approvalRepository;
    private final StepExecutor stepExecutor;
    private final WorkflowAuditService auditService;
    private final ObjectMapper objectMapper;

    @Transactional
    public WorkflowRun startRun(String workflowId, RunWorkflowRequest request, WorkflowTriggerType triggerType) {
        Workflow workflow = workflowRepository.findById(workflowId)
                .orElseThrow(() -> new IllegalArgumentException("Workflow not found: " + workflowId));
        if (workflow.getStatus() != WorkflowStatus.ACTIVE) {
            throw new WorkflowRunException("Workflow must be active before it can run");
        }
        String now = Instant.now().toString();
        WorkflowRun run = new WorkflowRun();
        run.setId(Ids.newId("wrun"));
        run.setWorkflowId(workflowId);
        run.setWorkflowVersion(workflow.getCurrentVersion());
        run.setStatus(WorkflowRunStatus.RUNNING);
        run.setTriggerType(triggerType);
        run.setInputJson(write(request == null ? null : request.input()));
        run.setIdempotencyKey(request == null ? null : request.idempotencyKey());
        run.setCreatedBy(request == null || request.createdBy() == null ? "user" : request.createdBy());
        run.setStartedAt(now);
        run.setUpdatedAt(now);
        WorkflowRun saved = runRepository.save(run);
        auditService.logEvent(workflowId, saved.getId(), null, "workflow_run_started", "running",
                "Workflow run started", RiskLevel.LOW, saved);
        return executeRun(saved.getId());
    }

    @Transactional
    public WorkflowRun executeRun(String runId) {
        WorkflowRun run = getRun(runId);
        if (run.getStatus() == WorkflowRunStatus.CANCELLED) {
            throw new WorkflowCancelledException("Workflow run is cancelled");
        }
        if (run.getStatus() == WorkflowRunStatus.PAUSED) {
            throw new WorkflowPausedException("Workflow run is paused");
        }
        Workflow workflow = workflowRepository.findById(run.getWorkflowId())
                .orElseThrow(() -> new WorkflowRunException("Workflow not found for run"));
        List<WorkflowStep> steps = stepRepository.findByWorkflowIdOrderByStepOrderAsc(workflow.getId());
        Set<String> completed = completedStepKeys(runId);

        for (WorkflowStep step : steps) {
            if (completed.contains(step.getStepKey())) {
                continue;
            }
            try {
                stepExecutor.executeStep(runId, step, workflow.getId());
            } catch (ApprovalRequiredException e) {
                run.setStatus(WorkflowRunStatus.WAITING_APPROVAL);
                run.setUpdatedAt(Instant.now().toString());
                runRepository.save(run);
                auditService.logEvent(workflow.getId(), runId, null, "workflow_waiting_approval", "waiting_approval",
                        "Workflow waiting for approval", RiskLevel.HIGH, Map.of("approval_request_id", e.getApprovalRequestId()));
                return run;
            } catch (RuntimeException e) {
                return failRun(runId, e.getMessage());
            }
        }
        return completeRun(runId, Map.of("status", "completed"));
    }

    @Transactional
    public WorkflowRun pauseRun(String runId) {
        WorkflowRun run = getRun(runId);
        run.setStatus(WorkflowRunStatus.PAUSED);
        run.setUpdatedAt(Instant.now().toString());
        auditService.logEvent(run.getWorkflowId(), runId, null, "workflow_paused", "paused",
                "Workflow run paused", RiskLevel.LOW, run);
        return runRepository.save(run);
    }

    @Transactional
    public WorkflowRun resumeRun(String runId) {
        WorkflowRun run = getRun(runId);
        if (run.getStatus() != WorkflowRunStatus.PAUSED && run.getStatus() != WorkflowRunStatus.WAITING_APPROVAL) {
            throw new WorkflowRunException("Only paused or waiting approval runs can resume");
        }
        run.setStatus(WorkflowRunStatus.RUNNING);
        run.setUpdatedAt(Instant.now().toString());
        runRepository.save(run);
        markApprovedWaitingSteps(runId);
        auditService.logEvent(run.getWorkflowId(), runId, null, "workflow_resumed", "running",
                "Workflow run resumed", RiskLevel.LOW, run);
        return executeRun(runId);
    }

    @Transactional
    public WorkflowRun cancelRun(String runId) {
        WorkflowRun run = getRun(runId);
        run.setStatus(WorkflowRunStatus.CANCELLED);
        run.setCompletedAt(Instant.now().toString());
        run.setUpdatedAt(run.getCompletedAt());
        auditService.logEvent(run.getWorkflowId(), runId, null, "workflow_cancelled", "cancelled",
                "Workflow run cancelled", RiskLevel.MEDIUM, run);
        return runRepository.save(run);
    }

    @Transactional
    public WorkflowRun retryRun(String runId) {
        WorkflowRun run = getRun(runId);
        if (run.getStatus() != WorkflowRunStatus.FAILED) {
            throw new WorkflowRunException("Only failed runs can be retried");
        }
        run.setStatus(WorkflowRunStatus.RUNNING);
        run.setUpdatedAt(Instant.now().toString());
        runRepository.save(run);
        return executeRun(runId);
    }

    @Transactional
    public WorkflowRun completeRun(String runId, Object output) {
        WorkflowRun run = getRun(runId);
        run.setStatus(WorkflowRunStatus.COMPLETED);
        run.setOutputJson(write(output));
        run.setCompletedAt(Instant.now().toString());
        run.setUpdatedAt(run.getCompletedAt());
        auditService.logEvent(run.getWorkflowId(), runId, null, "workflow_completed", "completed",
                "Workflow run completed", RiskLevel.LOW, output);
        return runRepository.save(run);
    }

    @Transactional
    public WorkflowRun failRun(String runId, String message) {
        WorkflowRun run = getRun(runId);
        run.setStatus(WorkflowRunStatus.FAILED);
        run.setErrorJson(write(Map.of("message", message)));
        run.setCompletedAt(Instant.now().toString());
        run.setUpdatedAt(run.getCompletedAt());
        auditService.logEvent(run.getWorkflowId(), runId, null, "workflow_failed", "failed",
                "Workflow run failed", RiskLevel.MEDIUM, run.getErrorJson());
        return runRepository.save(run);
    }

    public WorkflowRun getRun(String runId) {
        return runRepository.findById(runId)
                .orElseThrow(() -> new IllegalArgumentException("Workflow run not found: " + runId));
    }

    private Set<String> completedStepKeys(String runId) {
        Set<String> keys = new HashSet<>();
        for (WorkflowStepRun stepRun : stepRunRepository.findByRunIdOrderByStartedAtAsc(runId)) {
            if (stepRun.getStatus() == WorkflowStepRunStatus.SUCCESS) {
                keys.add(stepRun.getStepKey());
            }
        }
        return keys;
    }

    private void markApprovedWaitingSteps(String runId) {
        for (WorkflowStepRun stepRun : stepRunRepository.findByRunIdOrderByStartedAtAsc(runId)) {
            if (stepRun.getStatus() == WorkflowStepRunStatus.WAITING_APPROVAL && stepRun.getApprovalRequestId() != null) {
                approvalRepository.findById(stepRun.getApprovalRequestId()).ifPresent(approval -> {
                    if (approval.getStatus() == ApprovalStatus.APPROVED || approval.getStatus() == ApprovalStatus.MODIFIED) {
                        stepRun.setStatus(WorkflowStepRunStatus.SUCCESS);
                        stepRun.setOutputJson(write(Map.of("approval_request_id", approval.getId(), "decision", approval.getStatus())));
                        stepRun.setRedactedOutputJson(stepRun.getOutputJson());
                        stepRun.setCompletedAt(Instant.now().toString());
                        stepRun.setUpdatedAt(stepRun.getCompletedAt());
                        stepRunRepository.save(stepRun);
                    }
                });
            }
        }
    }

    private String write(Object value) {
        try {
            return objectMapper.writeValueAsString(value == null ? objectMapper.createObjectNode() : value);
        } catch (Exception e) {
            return "{}";
        }
    }
}
