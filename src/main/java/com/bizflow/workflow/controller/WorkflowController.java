package com.bizflow.workflow.controller;

import com.bizflow.workflow.dto.CreateWorkflowRequest;
import com.bizflow.workflow.dto.UpdateWorkflowRequest;
import com.bizflow.workflow.dto.WorkflowResponse;
import com.bizflow.workflow.dto.WorkflowVersionResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.service.WorkflowService;
import jakarta.validation.Valid;
import java.util.List;
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

@RestController
@RequestMapping("/api/workflows")
public class WorkflowController {
    private final WorkflowService workflowService;
    private final WorkflowMapper mapper;

    public WorkflowController(WorkflowService workflowService, WorkflowMapper mapper) {
        this.workflowService = workflowService;
        this.mapper = mapper;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public WorkflowResponse createWorkflow(@Valid @RequestBody CreateWorkflowRequest request) {
        return mapper.toResponse(workflowService.createWorkflow(request));
    }

    @GetMapping
    public List<WorkflowResponse> listWorkflows() {
        return workflowService.listWorkflows().stream().map(mapper::toResponse).toList();
    }

    @GetMapping("/{workflowId}")
    public WorkflowResponse getWorkflow(@PathVariable String workflowId) {
        return mapper.toResponse(workflowService.getWorkflow(workflowId));
    }

    @PutMapping("/{workflowId}")
    public WorkflowResponse updateWorkflow(@PathVariable String workflowId, @Valid @RequestBody UpdateWorkflowRequest request) {
        return mapper.toResponse(workflowService.updateWorkflow(workflowId, request));
    }

    @DeleteMapping("/{workflowId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteWorkflow(@PathVariable String workflowId) {
        workflowService.deleteWorkflow(workflowId);
    }

    @PostMapping("/{workflowId}/activate")
    public WorkflowResponse activateWorkflow(@PathVariable String workflowId) {
        return mapper.toResponse(workflowService.activateWorkflow(workflowId));
    }

    @PostMapping("/{workflowId}/pause")
    public WorkflowResponse pauseWorkflow(@PathVariable String workflowId) {
        return mapper.toResponse(workflowService.pauseWorkflow(workflowId));
    }

    @PostMapping("/{workflowId}/clone")
    @ResponseStatus(HttpStatus.CREATED)
    public WorkflowResponse cloneWorkflow(@PathVariable String workflowId) {
        return mapper.toResponse(workflowService.cloneWorkflow(workflowId));
    }

    @GetMapping("/{workflowId}/versions")
    public List<WorkflowVersionResponse> versions(@PathVariable String workflowId) {
        return workflowService.getVersions(workflowId).stream().map(mapper::toResponse).toList();
    }
}
