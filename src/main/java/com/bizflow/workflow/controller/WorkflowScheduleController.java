package com.bizflow.workflow.controller;

import com.bizflow.workflow.dto.ScheduleRequest;
import com.bizflow.workflow.dto.ScheduleResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.repository.WorkflowScheduleRepository;
import com.bizflow.workflow.service.WorkflowScheduler;
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
public class WorkflowScheduleController {
    private final WorkflowScheduler scheduler;
    private final WorkflowScheduleRepository repository;
    private final WorkflowMapper mapper;

    public WorkflowScheduleController(WorkflowScheduler scheduler, WorkflowScheduleRepository repository, WorkflowMapper mapper) {
        this.scheduler = scheduler;
        this.repository = repository;
        this.mapper = mapper;
    }

    @PostMapping("/{workflowId}/schedule")
    public ScheduleResponse create(@PathVariable String workflowId, @Valid @RequestBody ScheduleRequest request) {
        return mapper.toResponse(scheduler.registerSchedule(workflowId, request));
    }

    @PutMapping("/{workflowId}/schedule")
    public ScheduleResponse update(@PathVariable String workflowId, @Valid @RequestBody ScheduleRequest request) {
        repository.findByWorkflowId(workflowId).forEach(repository::delete);
        return mapper.toResponse(scheduler.registerSchedule(workflowId, request));
    }

    @DeleteMapping("/{workflowId}/schedule")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String workflowId) {
        repository.findByWorkflowId(workflowId).forEach(repository::delete);
    }

    @GetMapping("/schedules")
    public List<ScheduleResponse> list() {
        return scheduler.listSchedules().stream().map(mapper::toResponse).toList();
    }
}
