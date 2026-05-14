package com.bizflow.workflow.controller;

import com.bizflow.common.reactive.BlockingJpaBridge;
import com.bizflow.workflow.dto.EventBindingRequest;
import com.bizflow.workflow.dto.EventBindingResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.repository.WorkflowEventBindingRepository;
import com.bizflow.workflow.service.EventTriggerManager;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/workflows")
@RequiredArgsConstructor
public class WorkflowEventTriggerController {
    private final EventTriggerManager eventTriggerManager;
    private final WorkflowEventBindingRepository repository;
    private final WorkflowMapper mapper;
    private final BlockingJpaBridge blockingJpa;

    @PostMapping("/{workflowId}/event-binding")
    public Mono<EventBindingResponse> create(
            @PathVariable String workflowId,
            @Valid @RequestBody EventBindingRequest request
    ) {
        return blockingJpa.mono(() -> mapper.toResponse(eventTriggerManager.registerBinding(workflowId, request)));
    }

    @GetMapping("/event-bindings")
    public Flux<EventBindingResponse> list() {
        return blockingJpa.flux(() -> repository.findAll().stream().map(mapper::toResponse).toList());
    }

    @DeleteMapping("/event-bindings/{bindingId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> delete(@PathVariable String bindingId) {
        return blockingJpa.run(() -> repository.deleteById(bindingId));
    }
}
