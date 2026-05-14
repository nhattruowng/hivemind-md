package com.bizflow.agent_runtime.repository;

import com.bizflow.agent_runtime.domain.AgentTrace;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AgentTraceRepository extends JpaRepository<AgentTrace, String> {
    List<AgentTrace> findByRunIdOrderByCreatedAtAsc(String runId);
}
