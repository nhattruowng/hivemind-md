package com.bizflow.agent_runtime.repository;

import com.bizflow.agent_runtime.domain.AgentRunStep;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AgentRunStepRepository extends JpaRepository<AgentRunStep, String> {
    List<AgentRunStep> findByRunIdOrderByStepIndexAsc(String runId);
}
