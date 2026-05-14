package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowVersion;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowVersionRepository extends JpaRepository<WorkflowVersion, String> {
    List<WorkflowVersion> findByWorkflowIdOrderByVersionDesc(String workflowId);
}
