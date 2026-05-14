package com.bizflow.workflow.service;

import com.bizflow.workflow.domain.BackoffStrategy;
import com.bizflow.workflow.domain.RetryPolicy;
import org.springframework.stereotype.Service;

@Service
public class RetryPolicyEngine {
    public boolean shouldRetry(int attempt, RetryPolicy policy, String errorCode) {
        if (policy == null) {
            return false;
        }
        if (attempt >= policy.getMaxAttempts()) {
            return false;
        }
        String doNotRetry = policy.getDoNotRetryOnErrorsJson();
        return doNotRetry == null || errorCode == null || !doNotRetry.contains(errorCode);
    }

    public long calculateNextDelay(int attempt, RetryPolicy policy) {
        if (policy == null) {
            return 0;
        }
        long base = Math.max(0, policy.getInitialDelayMs());
        long delay = switch (policy.getBackoffStrategy() == null ? BackoffStrategy.FIXED : policy.getBackoffStrategy()) {
            case FIXED -> base;
            case LINEAR -> base * attempt;
            case EXPONENTIAL -> base * (long) Math.pow(2, Math.max(0, attempt - 1));
        };
        return Math.min(delay, policy.getMaxDelayMs());
    }

    public int recordAttempt(int currentAttempt) {
        return currentAttempt + 1;
    }
}
