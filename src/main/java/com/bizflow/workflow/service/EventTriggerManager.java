package com.bizflow.workflow.service;

import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.WorkflowEventBinding;
import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.bizflow.workflow.dto.EventBindingRequest;
import com.bizflow.workflow.dto.RunWorkflowRequest;
import com.bizflow.workflow.repository.WorkflowEventBindingRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.List;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class EventTriggerManager {
    private final WorkflowEventBindingRepository bindingRepository;
    private final WorkflowRunner workflowRunner;
    private final ObjectMapper objectMapper;
    private final ApplicationEventPublisher eventPublisher;

    public EventTriggerManager(WorkflowEventBindingRepository bindingRepository, WorkflowRunner workflowRunner,
                               ObjectMapper objectMapper, ApplicationEventPublisher eventPublisher) {
        this.bindingRepository = bindingRepository;
        this.workflowRunner = workflowRunner;
        this.objectMapper = objectMapper;
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public WorkflowEventBinding registerBinding(String workflowId, EventBindingRequest request) {
        String now = Instant.now().toString();
        WorkflowEventBinding binding = new WorkflowEventBinding();
        binding.setId(Ids.newId("web"));
        binding.setWorkflowId(workflowId);
        binding.setEventType(request.eventType());
        binding.setConditionJson(write(request.condition()));
        binding.setSourceScopeJson(write(request.sourceScope()));
        binding.setEnabled(true);
        binding.setCreatedAt(now);
        binding.setUpdatedAt(now);
        return bindingRepository.save(binding);
    }

    public void handleEvent(String eventType, JsonNode payload) {
        for (WorkflowEventBinding binding : matchWorkflow(eventType, payload)) {
            workflowRunner.startRun(binding.getWorkflowId(), new RunWorkflowRequest(payload, "event_trigger", Ids.newId("evt")),
                    WorkflowTriggerType.EVENT);
        }
    }

    public List<WorkflowEventBinding> matchWorkflow(String eventType, JsonNode payload) {
        return bindingRepository.findByEventTypeAndEnabledTrue(eventType);
    }

    public void publishLocalEvent(String eventType, JsonNode payload) {
        eventPublisher.publishEvent(new LocalWorkflowEvent(eventType, payload));
        handleEvent(eventType, payload);
    }

    private String write(Object value) {
        try {
            return objectMapper.writeValueAsString(value == null ? objectMapper.createObjectNode() : value);
        } catch (Exception e) {
            return "{}";
        }
    }

    public record LocalWorkflowEvent(String eventType, JsonNode payload) {
    }
}
