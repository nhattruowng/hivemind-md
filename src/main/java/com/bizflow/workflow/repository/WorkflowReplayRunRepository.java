package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowReplayRun;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowReplayRunRepository extends JpaRepository<WorkflowReplayRun, String> {
}
