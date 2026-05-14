package com.bizflow.agent_runtime.domain;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.Accessors;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Getter
@Setter
@NoArgsConstructor
@Accessors(chain = true)
@Entity
@Table(name = "agent_traces")
public class AgentTrace {
    @Id
    private String id;
    private String runId;
    private String eventType;
    @Column(columnDefinition = "TEXT")
    private String payloadJson;
    private String createdAt;
}
