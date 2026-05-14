package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowAuditEvent;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowAuditEventRepository extends JpaRepository<WorkflowAuditEvent, String> {
    List<WorkflowAuditEvent> findByRunIdOrderByCreatedAtAsc(String runId);
}
