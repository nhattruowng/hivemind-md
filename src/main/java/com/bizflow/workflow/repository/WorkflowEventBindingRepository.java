package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.WorkflowEventBinding;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface WorkflowEventBindingRepository extends JpaRepository<WorkflowEventBinding, String> {
    List<WorkflowEventBinding> findByEventTypeAndEnabledTrue(String eventType);
}
