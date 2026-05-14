package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowTrigger;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowTriggerRepository extends JpaRepository<WorkflowTrigger, String> {
    List<WorkflowTrigger> findByWorkflowIdAndEnabledTrue(String workflowId);
}
