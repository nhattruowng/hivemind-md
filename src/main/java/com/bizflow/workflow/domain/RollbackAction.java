package com.bizflow.workflow.domain;

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
@Table(name = "rollback_actions")
public class RollbackAction {
    @Id
    private String id;
    private String workflowId;
    private String stepKey;
    private String compensationType;
    @Column(columnDefinition = "TEXT")
    private String compensationJson;
    private boolean requiresApproval;
    private String status;
    private String createdAt;
    private String updatedAt;
}
