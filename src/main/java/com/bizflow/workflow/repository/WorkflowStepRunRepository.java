package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowStepRun;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowStepRunRepository extends JpaRepository<WorkflowStepRun, String> {
    List<WorkflowStepRun> findByRunIdOrderByStartedAtAsc(String runId);
}
