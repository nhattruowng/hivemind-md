package com.bizflow.tools.repository;

import com.bizflow.tools.domain.ToolDefinition;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ToolDefinitionRepository extends JpaRepository<ToolDefinition, String> {
    List<ToolDefinition> findByEnabledTrueOrderByNameAsc();
}
