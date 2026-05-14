package com.bizflow.models.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.SensitivityLevel;
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
@Table(name = "model_call_logs")
public class ModelCallLog {
    @Id
    private String id;
    private String runId;
    private String provider;
    private String modelName;
    private String taskType;
    @Enumerated(EnumType.STRING)
    private SensitivityLevel privacyLevel;
    private String status;
    private Integer promptTokens;
    private Integer completionTokens;
    @Column(columnDefinition = "TEXT")
    private String errorMessage;
    private String startedAt;
    private String completedAt;
}
