package com.bizflow.workflow.service;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.bizflow.approvals.domain.ApprovalRequest;
import com.bizflow.approvals.service.ApprovalService;
import com.bizflow.common.domain.ApprovalStatus;
import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.workflow.domain.WorkflowStep;
import com.bizflow.workflow.domain.WorkflowStepRun;
import com.bizflow.workflow.domain.WorkflowStepType;
import com.bizflow.workflow.exception.ApprovalRequiredException;
import com.bizflow.workflow.repository.WorkflowStepRunRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

class StepExecutorApprovalTest {
    @Test
    void highRiskToolStepRequiresApproval() {
        WorkflowStepRunRepository stepRunRepository = mock(WorkflowStepRunRepository.class);
        when(stepRunRepository.save(any(WorkflowStepRun.class))).thenAnswer(invocation -> invocation.getArgument(0));

        ApprovalService approvalService = mock(ApprovalService.class);
        ApprovalRequest approval = new ApprovalRequest();
        approval.setId("apr_test");
        approval.setStatus(ApprovalStatus.PENDING);
        when(approvalService.createApprovalRequest(any(), any(), any(), any(), any(), any(), any(), any(), any(), any()))
                .thenReturn(approval);

        StepExecutor executor = new StepExecutor(stepRunRepository, approvalService, mock(WorkflowAuditService.class), new ObjectMapper());
        WorkflowStep step = new WorkflowStep();
        step.setWorkflowId("wf_1");
        step.setStepKey("delete_file");
        step.setName("Delete file");
        step.setType(WorkflowStepType.TOOL_CALL);
        step.setInputJson("{\"tool_name\":\"delete_local_file\",\"path\":\"D:/danger.txt\"}");
        step.setRiskLevel(RiskLevel.HIGH);
        step.setPermissionLevel(PermissionLevel.EXECUTE_WITH_APPROVAL);
        step.setRequiresApproval(true);

        assertThatThrownBy(() -> executor.executeStep("run_1", step, "wf_1"))
                .isInstanceOf(ApprovalRequiredException.class)
                .hasMessageContaining("approval");
    }
}
