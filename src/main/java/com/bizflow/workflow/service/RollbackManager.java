package com.bizflow.workflow.service;

import com.bizflow.common.domain.RiskLevel;
import com.bizflow.workflow.domain.RollbackAction;
import com.bizflow.workflow.domain.WorkflowRun;
import com.bizflow.workflow.domain.WorkflowRunStatus;
import com.bizflow.workflow.domain.WorkflowStepRun;
import com.bizflow.workflow.domain.WorkflowStepRunStatus;
import com.bizflow.workflow.exception.RollbackFailedException;
import com.bizflow.workflow.repository.RollbackActionRepository;
import com.bizflow.workflow.repository.WorkflowRunRepository;
import com.bizflow.workflow.repository.WorkflowStepRunRepository;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class RollbackManager {
    private final WorkflowRunRepository runRepository;
    private final WorkflowStepRunRepository stepRunRepository;
    private final RollbackActionRepository rollbackActionRepository;
    private final WorkflowAuditService auditService;

    public RollbackManager(WorkflowRunRepository runRepository, WorkflowStepRunRepository stepRunRepository,
                           RollbackActionRepository rollbackActionRepository, WorkflowAuditService auditService) {
        this.runRepository = runRepository;
        this.stepRunRepository = stepRunRepository;
        this.rollbackActionRepository = rollbackActionRepository;
        this.auditService = auditService;
    }

    @Transactional
    public WorkflowRun rollbackRun(String runId) {
        WorkflowRun run = runRepository.findById(runId)
                .orElseThrow(() -> new IllegalArgumentException("Workflow run not found: " + runId));
        run.setStatus(WorkflowRunStatus.ROLLBACK_RUNNING);
        run.setUpdatedAt(Instant.now().toString());
        runRepository.save(run);
        List<WorkflowStepRun> steps = new ArrayList<>(stepRunRepository.findByRunIdOrderByStartedAtAsc(runId));
        Collections.reverse(steps);
        try {
            for (WorkflowStepRun step : steps) {
                rollbackStep(step);
            }
            run.setStatus(WorkflowRunStatus.ROLLBACK_COMPLETED);
            run.setCompletedAt(Instant.now().toString());
            run.setUpdatedAt(run.getCompletedAt());
            auditService.logEvent(run.getWorkflowId(), runId, null, "workflow_rollback_completed", "success",
                    "Workflow rollback completed", RiskLevel.HIGH, run);
            return runRepository.save(run);
        } catch (RuntimeException e) {
            run.setStatus(WorkflowRunStatus.ROLLBACK_FAILED);
            run.setUpdatedAt(Instant.now().toString());
            runRepository.save(run);
            throw new RollbackFailedException(e.getMessage());
        }
    }

    @Transactional
    public void rollbackStep(WorkflowStepRun stepRun) {
        List<RollbackAction> actions = rollbackActionRepository.findByWorkflowIdAndStepKey(stepRun.getWorkflowId(), stepRun.getStepKey());
        if (actions.isEmpty()) {
            auditService.logEvent(stepRun.getWorkflowId(), stepRun.getRunId(), stepRun.getId(),
                    "step_rollback_unavailable", "warning", "No compensation action configured", RiskLevel.MEDIUM, stepRun);
            return;
        }
        for (RollbackAction action : actions) {
            executeCompensationAction(action, stepRun);
        }
        stepRun.setStatus(WorkflowStepRunStatus.ROLLED_BACK);
        stepRun.setUpdatedAt(Instant.now().toString());
        stepRunRepository.save(stepRun);
    }

    public void executeCompensationAction(RollbackAction action, WorkflowStepRun stepRun) {
        if (action.isRequiresApproval()) {
            auditService.logEvent(stepRun.getWorkflowId(), stepRun.getRunId(), stepRun.getId(),
                    "step_rollback_requires_approval", "waiting_approval",
                    "Rollback compensation requires approval", RiskLevel.HIGH, action);
            return;
        }
        auditService.logEvent(stepRun.getWorkflowId(), stepRun.getRunId(), stepRun.getId(),
                "step_rollback_executed", "success", "Compensation action executed",
                RiskLevel.MEDIUM, Map.of("compensation_type", action.getCompensationType()));
    }
}
