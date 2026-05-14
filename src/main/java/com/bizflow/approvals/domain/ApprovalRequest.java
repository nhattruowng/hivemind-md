package com.bizflow.approvals.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.ApprovalStatus;
import com.bizflow.common.domain.RiskLevel;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Getter
@Setter
@NoArgsConstructor
@Accessors(chain = true)
@Entity
@Table(name = "approval_requests")
public class ApprovalRequest {
    @Id
    private String id;
    private String runId;
    private String workflowId;
    private String stepRunId;
    private String stepName;
    private String toolName;
    private String actionType;
    private String resourceType;
    private String resourceId;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    private String permissionLevel;
    @Enumerated(EnumType.STRING)
    private ApprovalStatus status;
    private String requestedBy;
    @Column(columnDefinition = "TEXT")
    private String previewJson;
    @Column(columnDefinition = "TEXT")
    private String inputPreviewJson;
    @Column(columnDefinition = "TEXT")
    private String outputPreviewJson;
    @Column(columnDefinition = "TEXT")
    private String expectedEffect;
    @Column(columnDefinition = "TEXT")
    private String diffPreviewJson;
    @Column(columnDefinition = "TEXT")
    private String actionJson;
    @Column(columnDefinition = "TEXT")
    private String decisionJson;
    @Column(columnDefinition = "TEXT")
    private String reason;
    private String createdAt;
    private String decidedAt;
    private String expiresAt;
}
