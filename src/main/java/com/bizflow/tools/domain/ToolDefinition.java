package com.bizflow.tools.domain;

import com.bizflow.common.domain.PermissionLevel;
import com.bizflow.common.domain.RiskLevel;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

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

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDisplayName() { return displayName; }
    public void setDisplayName(String displayName) { this.displayName = displayName; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    public String getInputSchemaJson() { return inputSchemaJson; }
    public void setInputSchemaJson(String inputSchemaJson) { this.inputSchemaJson = inputSchemaJson; }
    public String getOutputSchemaJson() { return outputSchemaJson; }
    public void setOutputSchemaJson(String outputSchemaJson) { this.outputSchemaJson = outputSchemaJson; }
    public PermissionLevel getPermissionLevel() { return permissionLevel; }
    public void setPermissionLevel(PermissionLevel permissionLevel) { this.permissionLevel = permissionLevel; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }
    public boolean isRequiresApproval() { return requiresApproval; }
    public void setRequiresApproval(boolean requiresApproval) { this.requiresApproval = requiresApproval; }
    public String getAllowedPathsJson() { return allowedPathsJson; }
    public void setAllowedPathsJson(String allowedPathsJson) { this.allowedPathsJson = allowedPathsJson; }
    public String getBlockedPathsJson() { return blockedPathsJson; }
    public void setBlockedPathsJson(String blockedPathsJson) { this.blockedPathsJson = blockedPathsJson; }
    public boolean isNetworkAccess() { return networkAccess; }
    public void setNetworkAccess(boolean networkAccess) { this.networkAccess = networkAccess; }
    public int getTimeoutMs() { return timeoutMs; }
    public void setTimeoutMs(int timeoutMs) { this.timeoutMs = timeoutMs; }
    public int getMaxRetries() { return maxRetries; }
    public void setMaxRetries(int maxRetries) { this.maxRetries = maxRetries; }
    public boolean isAuditEnabled() { return auditEnabled; }
    public void setAuditEnabled(boolean auditEnabled) { this.auditEnabled = auditEnabled; }
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
