package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.Workflow;
import com.bizflow.workflow.domain.WorkflowStatus;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowRepository extends JpaRepository<Workflow, String> {
    List<Workflow> findByStatusNotOrderByUpdatedAtDesc(WorkflowStatus status);
    List<Workflow> findByStatusOrderByUpdatedAtDesc(WorkflowStatus status);
}
