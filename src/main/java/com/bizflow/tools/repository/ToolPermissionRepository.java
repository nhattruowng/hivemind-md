package com.bizflow.tools.repository;

import com.bizflow.tools.domain.ToolPermission;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ToolPermissionRepository extends JpaRepository<ToolPermission, String> {
    List<ToolPermission> findByToolNameAndActionAndEnabledTrue(String toolName, String action);
}
