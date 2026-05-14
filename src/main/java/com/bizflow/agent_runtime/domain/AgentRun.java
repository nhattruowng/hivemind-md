package com.bizflow.agent_runtime.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.RiskLevel;
import com.bizflow.common.domain.RunStatus;
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
@Table(name = "agent_runs")
public class AgentRun {
    @Id
    private String id;
    private String userId;
    @Column(nullable = false, columnDefinition = "TEXT")
    private String userMessage;
    private String intent;
    @Enumerated(EnumType.STRING)
    private RunStatus status;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    private boolean requiresMemory;
    private boolean requiresTools;
    private boolean approvalRequired;
    private String approvalRequestId;
    private double confidence;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    private String createdAt;
    private String updatedAt;
    private String completedAt;
}
