package com.bizflow.workflow.domain;

public enum WorkflowStepType {
    TOOL_CALL,
    AGENT_TASK,
    CONDITION,
    LOOP,
    APPROVAL,
    DELAY,
    NOTIFICATION,
    TRANSFORM,
    MEMORY_SEARCH,
    MODEL_CALL,
    SUB_WORKFLOW
}
