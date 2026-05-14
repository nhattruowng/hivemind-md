package com.bizflow.workflow.service;

import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.Workflow;
import com.bizflow.workflow.domain.WorkflowStatus;
import com.bizflow.workflow.domain.WorkflowStep;
import com.bizflow.workflow.domain.WorkflowStepType;
import com.bizflow.workflow.domain.WorkflowTrigger;
import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.bizflow.workflow.domain.WorkflowVersion;
import com.bizflow.workflow.dto.CreateWorkflowRequest;
import com.bizflow.workflow.dto.UpdateWorkflowRequest;
import com.bizflow.workflow.exception.WorkflowValidationException;
import com.bizflow.workflow.repository.WorkflowRepository;
import com.bizflow.workflow.repository.WorkflowStepRepository;
import com.bizflow.workflow.repository.WorkflowTriggerRepository;
import com.bizflow.workflow.repository.WorkflowVersionRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.util.Iterator;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class WorkflowService {
    private final WorkflowRepository workflowRepository;
    private final WorkflowStepRepository stepRepository;
    private final WorkflowVersionRepository versionRepository;
    private final WorkflowTriggerRepository triggerRepository;
    private final WorkflowAuditService auditService;
    private final ObjectMapper objectMapper;

    public WorkflowService(WorkflowRepository workflowRepository, WorkflowStepRepository stepRepository,
                           WorkflowVersionRepository versionRepository, WorkflowTriggerRepository triggerRepository,
                           WorkflowAuditService auditService, ObjectMapper objectMapper) {
        this.workflowRepository = workflowRepository;
        this.stepRepository = stepRepository;
        this.versionRepository = versionRepository;
        this.triggerRepository = triggerRepository;
        this.auditService = auditService;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public Workflow createWorkflow(CreateWorkflowRequest request) {
        validateWorkflowDsl(request.definition());
        String now = Instant.now().toString();
        Workflow workflow = new Workflow();
        workflow.setId(Ids.newId("wf"));
        workflow.setName(request.name());
        workflow.setDescription(request.description());
        workflow.setStatus(WorkflowStatus.DRAFT);
        workflow.setTriggerType(request.triggerType());
        workflow.setCurrentVersion(1);
        workflow.setDefinitionJson(write(request.definition()));
        workflow.setInputSchemaJson(write(pathOrEmpty(request.definition(), "input_schema")));
        workflow.setOutputSchemaJson(write(pathOrEmpty(request.definition(), "output_schema")));
        workflow.setVariablesJson(write(pathOrEmpty(request.definition(), "variables")));
        workflow.setErrorPolicyJson(write(pathOrEmpty(request.definition(), "error_policy")));
        workflow.setApprovalPolicyJson(write(pathOrEmpty(request.definition(), "approval_policy")));
        workflow.setRetryPolicyJson(write(pathOrEmpty(request.definition(), "retry_policy")));
        workflow.setTimeoutPolicyJson(write(pathOrEmpty(request.definition(), "timeout_policy")));
        workflow.setCreatedBy(request.createdBy() == null ? "user" : request.createdBy());
        workflow.setCreatedAt(now);
        workflow.setUpdatedAt(now);
        Workflow saved = workflowRepository.save(workflow);
        saveSteps(saved.getId(), request.definition(), now);
        saveTrigger(saved.getId(), request.triggerType(), request.definition(), now);
        createVersion(saved, "create", saved.getCreatedBy());
        auditService.logEvent(saved.getId(), null, null, "workflow_created", "success",
                "Workflow created", RiskLevel.LOW, request.definition());
        return saved;
    }

    @Transactional
    public Workflow updateWorkflow(String workflowId, UpdateWorkflowRequest request) {
        validateWorkflowDsl(request.definition());
        Workflow workflow = getWorkflow(workflowId);
        if (workflow.getStatus() == WorkflowStatus.DELETED) {
            throw new WorkflowValidationException("Cannot update deleted workflow");
        }
        workflow.setName(request.name() == null ? workflow.getName() : request.name());
        workflow.setDescription(request.description());
        workflow.setDefinitionJson(write(request.definition()));
        workflow.setCurrentVersion(workflow.getCurrentVersion() + 1);
        workflow.setUpdatedAt(Instant.now().toString());
        Workflow saved = workflowRepository.save(workflow);
        stepRepository.deleteByWorkflowId(workflowId);
        saveSteps(workflowId, request.definition(), saved.getUpdatedAt());
        createVersion(saved, request.changeReason(), request.updatedBy() == null ? "user" : request.updatedBy());
        auditService.logEvent(saved.getId(), null, null, "workflow_updated", "success",
                "Workflow updated", RiskLevel.LOW, request.definition());
        return saved;
    }

    public List<Workflow> listWorkflows() {
        return workflowRepository.findByStatusNotOrderByUpdatedAtDesc(WorkflowStatus.DELETED);
    }

    public Workflow getWorkflow(String workflowId) {
        return workflowRepository.findById(workflowId)
                .orElseThrow(() -> new IllegalArgumentException("Workflow not found: " + workflowId));
    }

    @Transactional
    public Workflow activateWorkflow(String workflowId) {
        Workflow workflow = getWorkflow(workflowId);
        validateWorkflowDsl(read(workflow.getDefinitionJson()));
        workflow.setStatus(WorkflowStatus.ACTIVE);
        workflow.setUpdatedAt(Instant.now().toString());
        auditService.logEvent(workflowId, null, null, "workflow_activated", "success",
                "Workflow activated", RiskLevel.LOW, workflow);
        return workflowRepository.save(workflow);
    }

    @Transactional
    public Workflow pauseWorkflow(String workflowId) {
        Workflow workflow = getWorkflow(workflowId);
        workflow.setStatus(WorkflowStatus.PAUSED);
        workflow.setUpdatedAt(Instant.now().toString());
        auditService.logEvent(workflowId, null, null, "workflow_paused", "success",
                "Workflow paused", RiskLevel.LOW, workflow);
        return workflowRepository.save(workflow);
    }

    @Transactional
    public void deleteWorkflow(String workflowId) {
        Workflow workflow = getWorkflow(workflowId);
        workflow.setStatus(WorkflowStatus.DELETED);
        workflow.setDeletedAt(Instant.now().toString());
        workflow.setUpdatedAt(workflow.getDeletedAt());
        workflowRepository.save(workflow);
        auditService.logEvent(workflowId, null, null, "workflow_deleted", "success",
                "Workflow soft deleted", RiskLevel.MEDIUM, workflow);
    }

    @Transactional
    public Workflow cloneWorkflow(String workflowId) {
        Workflow source = getWorkflow(workflowId);
        CreateWorkflowRequest request = new CreateWorkflowRequest(
                source.getName() + " Copy",
                source.getDescription(),
                source.getTriggerType(),
                read(source.getDefinitionJson()),
                source.getCreatedBy()
        );
        return createWorkflow(request);
    }

    public List<WorkflowVersion> getVersions(String workflowId) {
        return versionRepository.findByWorkflowIdOrderByVersionDesc(workflowId);
    }

    public void validateWorkflowDsl(JsonNode definition) {
        if (definition == null || !definition.isObject()) {
            throw new WorkflowValidationException("Workflow definition must be a JSON object");
        }
        JsonNode steps = definition.get("steps");
        if (steps == null || !steps.isArray() || steps.isEmpty()) {
            throw new WorkflowValidationException("Workflow definition must contain a non-empty steps array");
        }
        for (JsonNode step : steps) {
            if (!step.hasNonNull("id") || !step.hasNonNull("type") || !step.hasNonNull("name")) {
                throw new WorkflowValidationException("Each workflow step requires id, name, and type");
            }
            enumValue(WorkflowStepType.class, step.get("type").asText());
        }
    }

    private void saveSteps(String workflowId, JsonNode definition, String now) {
        int order = 0;
        for (Iterator<JsonNode> it = definition.get("steps").elements(); it.hasNext();) {
            JsonNode item = it.next();
            WorkflowStep step = new WorkflowStep();
            step.setId(Ids.newId("wfs"));
            step.setWorkflowId(workflowId);
            step.setStepKey(item.get("id").asText());
            step.setName(item.get("name").asText());
            step.setType(enumValue(WorkflowStepType.class, item.get("type").asText()));
            step.setDescription(text(item, "description", null));
            step.setInputJson(write(pathOrEmpty(item, "input")));
            step.setOutputMappingJson(write(pathOrEmpty(item, "output_mapping")));
            step.setDependsOnJson(write(pathOrEmpty(item, "depends_on")));
            step.setConditionJson(write(pathOrEmpty(item, "condition")));
            step.setRetryPolicyJson(write(pathOrEmpty(item, "retry_policy")));
            step.setTimeoutMs(intValue(item, "timeout_ms", 30000));
            step.setRequiresApproval(booleanValue(item, "requires_approval", false));
            step.setRiskLevel(enumValue(RiskLevel.class, text(item, "risk_level", "LOW")));
            step.setPermissionLevel(enumValue(PermissionLevel.class, text(item, "permission_level", "READ_ONLY")));
            step.setCompensationJson(write(pathOrEmpty(item, "compensation")));
            step.setOnSuccessJson(write(pathOrEmpty(item, "on_success")));
            step.setOnFailureJson(write(pathOrEmpty(item, "on_failure")));
            step.setMetadataJson(write(pathOrEmpty(item, "metadata")));
            step.setStepOrder(order++);
            step.setCreatedAt(now);
            step.setUpdatedAt(now);
            stepRepository.save(step);
        }
    }

    private void saveTrigger(String workflowId, WorkflowTriggerType triggerType, JsonNode definition, String now) {
        WorkflowTrigger trigger = new WorkflowTrigger();
        trigger.setId(Ids.newId("wft"));
        trigger.setWorkflowId(workflowId);
        trigger.setTriggerType(triggerType);
        trigger.setConfigJson(write(pathOrEmpty(definition, "trigger")));
        trigger.setEnabled(true);
        trigger.setCreatedAt(now);
        trigger.setUpdatedAt(now);
        triggerRepository.save(trigger);
    }

    private void createVersion(Workflow workflow, String reason, String actor) {
        WorkflowVersion version = new WorkflowVersion();
        version.setId(Ids.newId("wfv"));
        version.setWorkflowId(workflow.getId());
        version.setVersion(workflow.getCurrentVersion());
        version.setDefinitionJson(workflow.getDefinitionJson());
        version.setChangeReason(reason);
        version.setCreatedBy(actor == null ? "user" : actor);
        version.setCreatedAt(Instant.now().toString());
        versionRepository.save(version);
    }

    private JsonNode read(String json) {
        try {
            return objectMapper.readTree(json);
        } catch (Exception e) {
            throw new WorkflowValidationException("Invalid workflow JSON");
        }
    }

    private String write(Object value) {
        try {
            return objectMapper.writeValueAsString(value == null ? objectMapper.createObjectNode() : value);
        } catch (Exception e) {
            throw new WorkflowValidationException("Cannot serialize workflow JSON");
        }
    }

    private JsonNode pathOrEmpty(JsonNode node, String field) {
        JsonNode value = node == null ? null : node.get(field);
        return value == null ? objectMapper.createObjectNode() : value;
    }

    private String text(JsonNode node, String field, String fallback) {
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? fallback : value.asText();
    }

    private int intValue(JsonNode node, String field, int fallback) {
        JsonNode value = node.get(field);
        return value == null || !value.canConvertToInt() ? fallback : value.asInt();
    }

    private boolean booleanValue(JsonNode node, String field, boolean fallback) {
        JsonNode value = node.get(field);
        return value == null || !value.isBoolean() ? fallback : value.asBoolean();
    }

    private <T extends Enum<T>> T enumValue(Class<T> type, String value) {
        return Enum.valueOf(type, value.toUpperCase().replace('-', '_'));
    }
}
