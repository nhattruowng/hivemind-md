package com.bizflow.tools.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
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
@Table(name = "tool_permissions")
public class ToolPermission {
    @Id
    private String id;
    private String toolName;
    private String action;
    private String scopeType;
    private String scopeValue;
    @Enumerated(EnumType.STRING)
    private PermissionLevel permissionLevel;
    @Enumerated(EnumType.STRING)
    private RiskLevel riskLevelCeiling;
    private boolean enabled;
    private String createdAt;
    private String updatedAt;
}
