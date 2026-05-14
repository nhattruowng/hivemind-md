package com.bizflow.tools.repository;

import com.bizflow.tools.domain.ToolCallLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ToolCallLogRepository extends JpaRepository<ToolCallLog, String> {
}
