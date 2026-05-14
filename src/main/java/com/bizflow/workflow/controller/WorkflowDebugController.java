package com.bizflow.workflow.controller;

import com.bizflow.workflow.dto.ReplayStepRequest;
import com.bizflow.workflow.dto.WorkflowRunResponse;
import com.bizflow.workflow.dto.WorkflowStepRunResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.repository.WorkflowStepRunRepository;
import com.bizflow.workflow.service.WorkflowReplayService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/workflows/runs/{runId}/steps")
public class WorkflowDebugController {
    private final WorkflowStepRunRepository stepRunRepository;
    private final WorkflowReplayService replayService;
    private final WorkflowMapper mapper;

    public WorkflowDebugController(WorkflowStepRunRepository stepRunRepository, WorkflowReplayService replayService,
                                   WorkflowMapper mapper) {
        this.stepRunRepository = stepRunRepository;
        this.replayService = replayService;
        this.mapper = mapper;
    }

    @GetMapping("/{stepRunId}")
    public WorkflowStepRunResponse getStep(@PathVariable String stepRunId) {
        return mapper.toResponse(stepRunRepository.findById(stepRunId)
                .orElseThrow(() -> new IllegalArgumentException("Step run not found: " + stepRunId)));
    }

    @GetMapping("/{stepRunId}/input")
    public Object getStepInput(@PathVariable String stepRunId) {
        return stepRunRepository.findById(stepRunId)
                .orElseThrow(() -> new IllegalArgumentException("Step run not found: " + stepRunId))
                .getRedactedInputJson();
    }

    @GetMapping("/{stepRunId}/output")
    public Object getStepOutput(@PathVariable String stepRunId) {
        return stepRunRepository.findById(stepRunId)
                .orElseThrow(() -> new IllegalArgumentException("Step run not found: " + stepRunId))
                .getRedactedOutputJson();
    }

    @PostMapping("/{stepRunId}/replay")
    public WorkflowRunResponse replay(@PathVariable String runId, @PathVariable String stepRunId,
                                      @RequestBody(required = false) ReplayStepRequest request) {
        return mapper.toResponse(replayService.replayFromStep(runId, stepRunId, request));
    }
}
