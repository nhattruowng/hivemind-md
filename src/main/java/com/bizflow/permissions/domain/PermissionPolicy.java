package com.bizflow.permissions.domain;

import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "permission_policies")
public class PermissionPolicy {
    @Id
    private String id;
    private String subjectType;
    private String subjectId;
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

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getSubjectType() { return subjectType; }
    public void setSubjectType(String subjectType) { this.subjectType = subjectType; }
    public String getSubjectId() { return subjectId; }
    public void setSubjectId(String subjectId) { this.subjectId = subjectId; }
    public String getToolName() { return toolName; }
    public void setToolName(String toolName) { this.toolName = toolName; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getScopeType() { return scopeType; }
    public void setScopeType(String scopeType) { this.scopeType = scopeType; }
    public String getScopeValue() { return scopeValue; }
    public void setScopeValue(String scopeValue) { this.scopeValue = scopeValue; }
    public PermissionLevel getPermissionLevel() { return permissionLevel; }
    public void setPermissionLevel(PermissionLevel permissionLevel) { this.permissionLevel = permissionLevel; }
    public RiskLevel getRiskLevelCeiling() { return riskLevelCeiling; }
    public void setRiskLevelCeiling(RiskLevel riskLevelCeiling) { this.riskLevelCeiling = riskLevelCeiling; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
