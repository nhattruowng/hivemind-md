package com.bizflow.workflow.controller;

import com.bizflow.common.reactive.BlockingJpaBridge;
import com.bizflow.workflow.dto.CreateWorkflowRequest;
import com.bizflow.workflow.dto.UpdateWorkflowRequest;
import com.bizflow.workflow.dto.WorkflowResponse;
import com.bizflow.workflow.dto.WorkflowVersionResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.service.WorkflowService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/workflows")
@RequiredArgsConstructor
public class WorkflowController {
    private final WorkflowService workflowService;
    private final WorkflowMapper mapper;
    private final BlockingJpaBridge blockingJpa;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<WorkflowResponse> createWorkflow(@Valid @RequestBody CreateWorkflowRequest request) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowService.createWorkflow(request)));
    }

    @GetMapping
    public Flux<WorkflowResponse> listWorkflows() {
        return blockingJpa.flux(() -> workflowService.listWorkflows().stream().map(mapper::toResponse).toList());
    }

    @GetMapping("/{workflowId}")
    public Mono<WorkflowResponse> getWorkflow(@PathVariable String workflowId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowService.getWorkflow(workflowId)));
    }

    @PutMapping("/{workflowId}")
    public Mono<WorkflowResponse> updateWorkflow(
            @PathVariable String workflowId,
            @Valid @RequestBody UpdateWorkflowRequest request
    ) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowService.updateWorkflow(workflowId, request)));
    }

    @DeleteMapping("/{workflowId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> deleteWorkflow(@PathVariable String workflowId) {
        return blockingJpa.run(() -> workflowService.deleteWorkflow(workflowId));
    }

    @PostMapping("/{workflowId}/activate")
    public Mono<WorkflowResponse> activateWorkflow(@PathVariable String workflowId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowService.activateWorkflow(workflowId)));
    }

    @PostMapping("/{workflowId}/pause")
    public Mono<WorkflowResponse> pauseWorkflow(@PathVariable String workflowId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowService.pauseWorkflow(workflowId)));
    }

    @PostMapping("/{workflowId}/clone")
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<WorkflowResponse> cloneWorkflow(@PathVariable String workflowId) {
        return blockingJpa.mono(() -> mapper.toResponse(workflowService.cloneWorkflow(workflowId)));
    }

    @GetMapping("/{workflowId}/versions")
    public Flux<WorkflowVersionResponse> versions(@PathVariable String workflowId) {
        return blockingJpa.flux(() -> workflowService.getVersions(workflowId).stream().map(mapper::toResponse).toList());
    }
}
