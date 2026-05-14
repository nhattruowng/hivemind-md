package com.bizflow.audit.repository;

import com.bizflow.audit.domain.AuditLog;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AuditLogRepository extends JpaRepository<AuditLog, String> {
    List<AuditLog> findTop100ByOrderByCreatedAtDesc();
    List<AuditLog> findByRunIdOrderByCreatedAtAsc(String runId);
}
