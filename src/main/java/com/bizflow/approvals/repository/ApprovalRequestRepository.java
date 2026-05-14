package com.bizflow.approvals.repository;

import com.bizflow.approvals.domain.ApprovalRequest;
import com.bizflow.common.domain.ApprovalStatus;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ApprovalRequestRepository extends JpaRepository<ApprovalRequest, String> {
    List<ApprovalRequest> findByStatusOrderByCreatedAtDesc(ApprovalStatus status);
}
