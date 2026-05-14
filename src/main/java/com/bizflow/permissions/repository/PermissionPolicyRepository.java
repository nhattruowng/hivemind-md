package com.bizflow.permissions.repository;

import com.bizflow.permissions.domain.PermissionPolicy;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PermissionPolicyRepository extends JpaRepository<PermissionPolicy, String> {
    List<PermissionPolicy> findByToolNameAndActionAndEnabledTrue(String toolName, String action);
}
