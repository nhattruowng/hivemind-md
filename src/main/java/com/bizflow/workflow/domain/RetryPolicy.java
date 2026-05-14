package com.bizflow.workflow.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

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
}
