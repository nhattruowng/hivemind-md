package com.bizflow.workflow.service;

import com.bizflow.common.util.Ids;
import com.bizflow.workflow.domain.WorkflowSchedule;
import com.bizflow.workflow.domain.WorkflowTriggerType;
import com.bizflow.workflow.dto.RunWorkflowRequest;
import com.bizflow.workflow.dto.ScheduleRequest;
import com.bizflow.workflow.repository.WorkflowScheduleRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.scheduling.support.CronExpression;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class WorkflowScheduler {
    private final WorkflowScheduleRepository scheduleRepository;
    private final WorkflowRunner workflowRunner;
    private final ObjectMapper objectMapper;

    @Transactional
    public WorkflowSchedule registerSchedule(String workflowId, ScheduleRequest request) {
        String now = Instant.now().toString();
        WorkflowSchedule schedule = new WorkflowSchedule();
        schedule.setId(Ids.newId("wsch"));
        schedule.setWorkflowId(workflowId);
        schedule.setCronExpression(request.cronExpression());
        schedule.setTimezone(request.timezone());
        schedule.setNextRunAt(calculateNextRun(request.cronExpression(), request.timezone()));
        schedule.setEnabled(true);
        schedule.setCreatedAt(now);
        schedule.setUpdatedAt(now);
        return scheduleRepository.save(schedule);
    }

    public String calculateNextRun(String cronExpression, String timezone) {
        CronExpression cron = CronExpression.parse(cronExpression);
        ZonedDateTime next = cron.next(ZonedDateTime.now(ZoneId.of(timezone)));
        return next == null ? null : next.toInstant().toString();
    }

    @Scheduled(fixedDelay = 30000)
    @Transactional
    public void triggerDueWorkflows() {
        String now = Instant.now().toString();
        for (WorkflowSchedule schedule : scheduleRepository.findByEnabledTrueOrderByNextRunAtAsc()) {
            if (schedule.getNextRunAt() != null && schedule.getNextRunAt().compareTo(now) <= 0) {
                workflowRunner.startRun(schedule.getWorkflowId(), new RunWorkflowRequest(
                        objectMapper.createObjectNode(), "scheduler", Ids.newId("sched")
                ), WorkflowTriggerType.SCHEDULE);
                schedule.setLastRunAt(now);
                schedule.setNextRunAt(calculateNextRun(schedule.getCronExpression(), schedule.getTimezone()));
                schedule.setUpdatedAt(now);
                scheduleRepository.save(schedule);
            }
        }
    }

    public List<WorkflowSchedule> listSchedules() {
        return scheduleRepository.findByEnabledTrueOrderByNextRunAtAsc();
    }
}
