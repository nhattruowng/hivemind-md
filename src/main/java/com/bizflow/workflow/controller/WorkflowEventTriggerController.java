package com.bizflow.workflow.controller;

import com.bizflow.workflow.dto.EventBindingRequest;
import com.bizflow.workflow.dto.EventBindingResponse;
import com.bizflow.workflow.mapper.WorkflowMapper;
import com.bizflow.workflow.repository.WorkflowEventBindingRepository;
import com.bizflow.workflow.service.EventTriggerManager;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/workflows")
public class WorkflowEventTriggerController {
    private final EventTriggerManager eventTriggerManager;
    private final WorkflowEventBindingRepository repository;
    private final WorkflowMapper mapper;

    public WorkflowEventTriggerController(EventTriggerManager eventTriggerManager, WorkflowEventBindingRepository repository,
                                          WorkflowMapper mapper) {
        this.eventTriggerManager = eventTriggerManager;
        this.repository = repository;
        this.mapper = mapper;
    }

    @PostMapping("/{workflowId}/event-binding")
    public EventBindingResponse create(@PathVariable String workflowId, @Valid @RequestBody EventBindingRequest request) {
        return mapper.toResponse(eventTriggerManager.registerBinding(workflowId, request));
    }

    @GetMapping("/event-bindings")
    public List<EventBindingResponse> list() {
        return repository.findAll().stream().map(mapper::toResponse).toList();
    }

    @DeleteMapping("/event-bindings/{bindingId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String bindingId) {
        repository.deleteById(bindingId);
    }
}
