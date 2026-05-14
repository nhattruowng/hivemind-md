package com.bizflow.models.repository;

import com.bizflow.models.domain.ModelCallLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelCallLogRepository extends JpaRepository<ModelCallLog, String> {
}
