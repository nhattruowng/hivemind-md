package com.bizflow;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class BizFlowLocalAgentApplication {
    public static void main(String[] args) {
        SpringApplication.run(BizFlowLocalAgentApplication.class, args);
    }
}
