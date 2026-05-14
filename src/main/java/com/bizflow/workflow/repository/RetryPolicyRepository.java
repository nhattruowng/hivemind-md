package com.bizflow.workflow.repository;

import com.bizflow.workflow.domain.RetryPolicy;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RetryPolicyRepository extends JpaRepository<RetryPolicy, String> {
    Optional<RetryPolicy> findByOwnerTypeAndOwnerId(String ownerType, String ownerId);
}
