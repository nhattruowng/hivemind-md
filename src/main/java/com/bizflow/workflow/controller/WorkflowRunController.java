package com.bizflow.workflow.controller;

import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.bizflow.workflow.dto.RunWorkflowRequest;
import com.bizflow.workflow.dto.WorkflowRunResponse;
import com.bizflow.workflow.dto.WorkflowTimelineResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.repository.WorkflowStepRunRepository;
import com.bizflow.workflow.service.RollbackManager;
import com.bizflow.workflow.service.WorkflowAuditService;
import com.bizflow.workflow.service.WorkflowRunner;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/workflows")
public class WorkflowRunController {
    private final WorkflowRunner workflowRunner;
    private final RollbackManager rollbackManager;
    private final WorkflowAuditService auditService;
    private final WorkflowStepRunRepository stepRunRepository;
    private final WorkflowMapper mapper;

    public WorkflowRunController(WorkflowRunner workflowRunner, RollbackManager rollbackManager,
                                 WorkflowAuditService auditService, WorkflowStepRunRepository stepRunRepository,
                                 WorkflowMapper mapper) {
        this.workflowRunner = workflowRunner;
        this.rollbackManager = rollbackManager;
        this.auditService = auditService;
        this.stepRunRepository = stepRunRepository;
        this.mapper = mapper;
    }

    @PostMapping("/{workflowId}/run")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public WorkflowRunResponse run(@PathVariable String workflowId, @Valid @RequestBody(required = false) RunWorkflowRequest request) {
        return mapper.toResponse(workflowRunner.startRun(workflowId, request, WorkflowTriggerType.MANUAL));
    }

    @GetMapping("/runs/{runId}")
    public WorkflowRunResponse getRun(@PathVariable String runId) {
        return mapper.toResponse(workflowRunner.getRun(runId));
    }

    @GetMapping("/runs/{runId}/timeline")
    public WorkflowTimelineResponse timeline(@PathVariable String runId) {
        return new WorkflowTimelineResponse(
                runId,
                auditService.getTimeline(runId).stream().map(mapper::toResponse).toList(),
                stepRunRepository.findByRunIdOrderByStartedAtAsc(runId).stream().map(mapper::toResponse).toList()
        );
    }

    @PostMapping("/runs/{runId}/pause")
    public WorkflowRunResponse pause(@PathVariable String runId) {
        return mapper.toResponse(workflowRunner.pauseRun(runId));
    }

    @PostMapping("/runs/{runId}/resume")
    public WorkflowRunResponse resume(@PathVariable String runId) {
        return mapper.toResponse(workflowRunner.resumeRun(runId));
    }

    @PostMapping("/runs/{runId}/cancel")
    public WorkflowRunResponse cancel(@PathVariable String runId) {
        return mapper.toResponse(workflowRunner.cancelRun(runId));
    }

    @PostMapping("/runs/{runId}/retry")
    public WorkflowRunResponse retry(@PathVariable String runId) {
        return mapper.toResponse(workflowRunner.retryRun(runId));
    }

    @PostMapping("/runs/{runId}/rollback")
    public WorkflowRunResponse rollback(@PathVariable String runId) {
        return mapper.toResponse(rollbackManager.rollbackRun(runId));
    }
}
