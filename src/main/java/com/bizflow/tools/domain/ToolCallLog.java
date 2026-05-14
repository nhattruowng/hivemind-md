package com.bizflow.tools.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.PermissionDecisionType;
import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.domain.ToolCallStatus;
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
@Table(name = "tool_call_logs")
public class ToolCallLog {
    @Id
    private String id;
    private String runId;
    private String toolName;
    @Enumerated(EnumType.STRING)
    private ToolCallStatus status;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    @Enumerated(EnumType.STRING)
    private PermissionDecisionType permissionDecision;
    @Column(columnDefinition = "TEXT")
    private String redactedInputJson;
    @Column(columnDefinition = "TEXT")
    private String redactedOutputJson;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    private String approvalRequestId;
    private String startedAt;
    private String completedAt;
}
