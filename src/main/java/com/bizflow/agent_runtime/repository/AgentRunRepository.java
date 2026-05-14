package com.bizflow.agent_runtime.repository;

import com.bizflow.agent_runtime.domain.AgentRun;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AgentRunRepository extends JpaRepository<AgentRun, String> {
}
