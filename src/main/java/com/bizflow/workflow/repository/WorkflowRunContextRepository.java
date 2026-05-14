package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowRunContext;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowRunContextRepository extends JpaRepository<WorkflowRunContext, String> {
    List<WorkflowRunContext> findByRunId(String runId);
}
