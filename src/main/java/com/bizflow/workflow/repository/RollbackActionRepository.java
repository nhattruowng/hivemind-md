package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.RollbackAction;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RollbackActionRepository extends JpaRepository<RollbackAction, String> {
    List<RollbackAction> findByWorkflowIdAndStepKey(String workflowId, String stepKey);
}
