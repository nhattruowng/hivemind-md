package com.bizflow.workflow.service;

import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.WorkflowReplayRun;
import com.bizflow.workflow.domain.WorkflowRun;
import com.bizflow.workflow.dto.ReplayStepRequest;
import com.bizflow.workflow.dto.RunWorkflowRequest;
import com.bizflow.workflow.repository.WorkflowReplayRunRepository;
import com.bizflow.workflow.repository.WorkflowRunContextRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class WorkflowReplayService {
    private final WorkflowRunner workflowRunner;
    private final WorkflowReplayRunRepository replayRunRepository;
    private final WorkflowRunContextRepository contextRepository;
    private final ObjectMapper objectMapper;

    public WorkflowReplayService(WorkflowRunner workflowRunner, WorkflowReplayRunRepository replayRunRepository,
                                 WorkflowRunContextRepository contextRepository, ObjectMapper objectMapper) {
        this.workflowRunner = workflowRunner;
        this.replayRunRepository = replayRunRepository;
        this.contextRepository = contextRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public WorkflowRun replayFromStep(String parentRunId, String stepRunId, ReplayStepRequest request) {
        WorkflowRun parent = workflowRunner.getRun(parentRunId);
        WorkflowRun replay = workflowRunner.startRun(parent.getWorkflowId(), new RunWorkflowRequest(
                request == null ? null : request.inputOverride(),
                request == null || request.createdBy() == null ? "user" : request.createdBy(),
                Ids.newId("replay")
        ), parent.getTriggerType());
        WorkflowReplayRun record = new WorkflowReplayRun();
        record.setId(Ids.newId("wrp"));
        record.setParentRunId(parentRunId);
        record.setReplayRunId(replay.getId());
        record.setFromStepRunId(stepRunId);
        record.setInputOverrideJson(write(request == null ? null : request.inputOverride()));
        record.setCreatedBy(request == null || request.createdBy() == null ? "user" : request.createdBy());
        record.setCreatedAt(Instant.now().toString());
        replayRunRepository.save(record);
        return replay;
    }

    public Object loadPreviousContext(String runId) {
        return contextRepository.findByRunId(runId);
    }

    private String write(Object value) {
        try {
            return objectMapper.writeValueAsString(value == null ? objectMapper.createObjectNode() : value);
        } catch (Exception e) {
            return "{}";
        }
    }
}
