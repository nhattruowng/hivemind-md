package com.bizflow.workflow.service;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;

import com.bizflow.workflow.exception.WorkflowValidationException;
import com.bizflow.workflow.repository.WorkflowRepository;
import com.bizflow.workflow.repository.WorkflowStepRepository;
import com.bizflow.workflow.repository.WorkflowTriggerRepository;
import com.bizflow.workflow.repository.WorkflowVersionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

class WorkflowServiceValidationTest {
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final WorkflowService service = new WorkflowService(
            mock(WorkflowRepository.class),
            mock(WorkflowStepRepository.class),
            mock(WorkflowVersionRepository.class),
            mock(WorkflowTriggerRepository.class),
            mock(WorkflowAuditService.class),
            objectMapper
    );

    @Test
    void rejectsWorkflowWithoutSteps() throws Exception {
        assertThatThrownBy(() -> service.validateWorkflowDsl(objectMapper.readTree("{\"steps\":[]}")))
                .isInstanceOf(WorkflowValidationException.class)
                .hasMessageContaining("steps");
    }

    @Test
    void rejectsStepWithoutType() throws Exception {
        assertThatThrownBy(() -> service.validateWorkflowDsl(objectMapper.readTree("""
                {"steps":[{"id":"s1","name":"Broken"}]}
                """)))
                .isInstanceOf(WorkflowValidationException.class);
    }
}
