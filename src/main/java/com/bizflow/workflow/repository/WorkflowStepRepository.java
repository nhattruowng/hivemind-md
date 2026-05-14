package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowStep;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowStepRepository extends JpaRepository<WorkflowStep, String> {
    List<WorkflowStep> findByWorkflowIdOrderByStepOrderAsc(String workflowId);
    void deleteByWorkflowId(String workflowId);
}
