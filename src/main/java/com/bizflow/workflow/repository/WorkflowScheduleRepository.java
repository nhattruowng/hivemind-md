package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowSchedule;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowScheduleRepository extends JpaRepository<WorkflowSchedule, String> {
    List<WorkflowSchedule> findByEnabledTrueOrderByNextRunAtAsc();
    List<WorkflowSchedule> findByWorkflowId(String workflowId);
}
