package com.bizflow.workflow.controller;

import com.bizflow.common.reactive.BlockingJpaBridge;
import com.bizflow.workflow.dto.ScheduleRequest;
import com.bizflow.workflow.dto.ScheduleResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.repository.WorkflowScheduleRepository;
import com.bizflow.workflow.service.WorkflowScheduler;
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
public class WorkflowScheduleController {
    private final WorkflowScheduler scheduler;
    private final WorkflowScheduleRepository repository;
    private final WorkflowMapper mapper;
    private final BlockingJpaBridge blockingJpa;

    @PostMapping("/{workflowId}/schedule")
    public Mono<ScheduleResponse> create(
            @PathVariable String workflowId,
            @Valid @RequestBody ScheduleRequest request
    ) {
        return blockingJpa.mono(() -> mapper.toResponse(scheduler.registerSchedule(workflowId, request)));
    }

    @PutMapping("/{workflowId}/schedule")
    public Mono<ScheduleResponse> update(
            @PathVariable String workflowId,
            @Valid @RequestBody ScheduleRequest request
    ) {
        return blockingJpa.mono(() -> {
            repository.findByWorkflowId(workflowId).forEach(repository::delete);
            return mapper.toResponse(scheduler.registerSchedule(workflowId, request));
        });
    }

    @DeleteMapping("/{workflowId}/schedule")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> delete(@PathVariable String workflowId) {
        return blockingJpa.run(() -> repository.findByWorkflowId(workflowId).forEach(repository::delete));
    }

    @GetMapping("/schedules")
    public Flux<ScheduleResponse> list() {
        return blockingJpa.flux(() -> scheduler.listSchedules().stream().map(mapper::toResponse).toList());
    }
}
