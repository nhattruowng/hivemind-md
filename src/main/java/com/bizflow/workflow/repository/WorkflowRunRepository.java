package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowRun;
import com.bizflow.workflow.domain.WorkflowRunStatus;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowRunRepository extends JpaRepository<WorkflowRun, String> {
    List<WorkflowRun> findByWorkflowIdOrderByStartedAtDesc(String workflowId);
    List<WorkflowRun> findByStatus(WorkflowRunStatus status);
}
