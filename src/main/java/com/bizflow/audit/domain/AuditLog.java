package com.bizflow.audit.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

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
@Table(name = "audit_logs")
public class AuditLog {
    @Id
    private String id;
    private String runId;
    private String eventType;
    private String actorType;
    private String actorId;
    private String resourceType;
    private String resourceId;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    private String status;
    @Column(columnDefinition = "TEXT")
    private String summary;
    @Column(columnDefinition = "TEXT")
    private String redactedPayloadJson;
    private String traceId;
    private String createdAt;
}
