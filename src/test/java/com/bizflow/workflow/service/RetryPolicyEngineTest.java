package com.bizflow.workflow.service;

import static org.assertj.core.api.Assertions.assertThat;

import com.bizflow.workflow.domain.BackoffStrategy;
import com.bizflow.workflow.domain.RetryPolicy;
import org.junit.jupiter.api.Test;

class RetryPolicyEngineTest {
    private final RetryPolicyEngine engine = new RetryPolicyEngine();

    @Test
    void calculatesExponentialBackoffWithinMaxDelay() {
        RetryPolicy policy = new RetryPolicy();
        policy.setMaxAttempts(4);
        policy.setBackoffStrategy(BackoffStrategy.EXPONENTIAL);
        policy.setInitialDelayMs(1000);
        policy.setMaxDelayMs(2500);

        assertThat(engine.calculateNextDelay(1, policy)).isEqualTo(1000);
        assertThat(engine.calculateNextDelay(2, policy)).isEqualTo(2000);
        assertThat(engine.calculateNextDelay(3, policy)).isEqualTo(2500);
    }

    @Test
    void stopsRetryWhenAttemptLimitReached() {
        RetryPolicy policy = new RetryPolicy();
        policy.setMaxAttempts(2);
        policy.setDoNotRetryOnErrorsJson("[]");

        assertThat(engine.shouldRetry(1, policy, "TOOL_TIMEOUT")).isTrue();
        assertThat(engine.shouldRetry(2, policy, "TOOL_TIMEOUT")).isFalse();
    }
}
