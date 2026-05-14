package com.bizflow.tools.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.PermissionLevel;
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
@Table(name = "tool_definitions")
public class ToolDefinition {
    @Id
    private String name;
    private String displayName;
    @Column(columnDefinition = "TEXT")
    private String description;
    private String category;
    private String version;
    @Column(columnDefinition = "TEXT")
    private String inputSchemaJson;
    @Column(columnDefinition = "TEXT")
    private String outputSchemaJson;
    @Enumerated(EnumType.STRING)
    private PermissionLevel permissionLevel;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevel;
    private boolean requiresApproval;
    @Column(columnDefinition = "TEXT")
    private String allowedPathsJson;
    @Column(columnDefinition = "TEXT")
    private String blockedPathsJson;
    private boolean networkAccess;
    private int timeoutMs;
    private int maxRetries;
    private boolean auditEnabled;
    private boolean enabled;
    private String createdAt;
    private String updatedAt;
}
