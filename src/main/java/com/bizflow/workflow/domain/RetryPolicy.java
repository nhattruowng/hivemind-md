package com.bizflow.workflow.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "retry_policies")
public class RetryPolicy {
    @Id
    private String id;
    private String ownerType;
    private String ownerId;
    private int maxAttempts;
    @Enumerated(EnumType.STRING)
    private BackoffStrategy backoffStrategy;
    private long initialDelayMs;
    private long maxDelayMs;
    @Column(columnDefinition = "TEXT")
    private String retryOnErrorsJson;
    @Column(columnDefinition = "TEXT")
    private String doNotRetryOnErrorsJson;
    private String createdAt;
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getOwnerType() { return ownerType; }
    public void setOwnerType(String ownerType) { this.ownerType = ownerType; }
    public String getOwnerId() { return ownerId; }
    public void setOwnerId(String ownerId) { this.ownerId = ownerId; }
    public int getMaxAttempts() { return maxAttempts; }
    public void setMaxAttempts(int maxAttempts) { this.maxAttempts = maxAttempts; }
    public BackoffStrategy getBackoffStrategy() { return backoffStrategy; }
    public void setBackoffStrategy(BackoffStrategy backoffStrategy) { this.backoffStrategy = backoffStrategy; }
    public long getInitialDelayMs() { return initialDelayMs; }
    public void setInitialDelayMs(long initialDelayMs) { this.initialDelayMs = initialDelayMs; }
    public long getMaxDelayMs() { return maxDelayMs; }
    public void setMaxDelayMs(long maxDelayMs) { this.maxDelayMs = maxDelayMs; }
    public String getRetryOnErrorsJson() { return retryOnErrorsJson; }
    public void setRetryOnErrorsJson(String retryOnErrorsJson) { this.retryOnErrorsJson = retryOnErrorsJson; }
    public String getDoNotRetryOnErrorsJson() { return doNotRetryOnErrorsJson; }
    public void setDoNotRetryOnErrorsJson(String doNotRetryOnErrorsJson) { this.doNotRetryOnErrorsJson = doNotRetryOnErrorsJson; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
