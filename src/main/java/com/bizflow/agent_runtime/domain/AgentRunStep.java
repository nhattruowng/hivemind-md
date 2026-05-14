package com.bizflow.agent_runtime.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.StepStatus;
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
@Table(name = "agent_run_steps")
public class AgentRunStep {
    @Id
    private String id;
    private String runId;
    private int stepIndex;
    private String stepType;
    private String toolName;
    @Enumerated(EnumType.STRING)
    private StepStatus status;
    @Column(columnDefinition = "TEXT")
    private String inputJson;
    @Column(columnDefinition = "TEXT")
    private String outputJson;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    private String createdAt;
    private String completedAt;
}
