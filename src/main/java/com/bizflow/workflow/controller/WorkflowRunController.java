package com.bizflow.workflow.controller;

import com.bizflow.common.reactive.BlockingJpaBridge;
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
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/workflows")
@RequiredArgsConstructor
public class WorkflowRunController {
    private final WorkflowRunner workflowRunner;
    private final RollbackManager rollbackManager;
    private final WorkflowAuditService auditService;
    private final WorkflowStepRunRepository stepRunRepository;
    private final WorkflowMapper mapper;
    private final BlockingJpaBridge blockingJpa;

    @PostMapping("/{workflowId}/run")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public Mono<WorkflowRunResponse> run(
            @PathVariable String workflowId,
            @Valid @RequestBody(required = false) RunWorkflowRequest request
    ) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowRunner.startRun(workflowId, request, WorkflowTriggerType.MANUAL)));
    }

    @GetMapping("/runs/{runId}")
    public Mono<WorkflowRunResponse> getRun(@PathVariable String runId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowRunner.getRun(runId)));
    }

    @GetMapping("/runs/{runId}/timeline")
    public Mono<WorkflowTimelineResponse> timeline(@PathVariable String runId) {
        return blockingJpa.mono(() -> new WorkflowTimelineResponse(
                runId,
                auditService.getTimeline(runId).stream().map(mapper::toResponse).toList(),
                stepRunRepository.findByRunIdOrderByStartedAtAsc(runId).stream().map(mapper::toResponse).toList()
        ));
    }

    @PostMapping("/runs/{runId}/pause")
    public Mono<WorkflowRunResponse> pause(@PathVariable String runId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowRunner.pauseRun(runId)));
    }

    @PostMapping("/runs/{runId}/resume")
    public Mono<WorkflowRunResponse> resume(@PathVariable String runId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowRunner.resumeRun(runId)));
    }

    @PostMapping("/runs/{runId}/cancel")
    public Mono<WorkflowRunResponse> cancel(@PathVariable String runId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowRunner.cancelRun(runId)));
    }

    @PostMapping("/runs/{runId}/retry")
    public Mono<WorkflowRunResponse> retry(@PathVariable String runId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowRunner.retryRun(runId)));
    }

    @PostMapping("/runs/{runId}/rollback")
    public Mono<WorkflowRunResponse> rollback(@PathVariable String runId) {
        return blockingJpa.mono(() -> mapper.toResponse(rollbackManager.rollbackRun(runId)));
    }
}
