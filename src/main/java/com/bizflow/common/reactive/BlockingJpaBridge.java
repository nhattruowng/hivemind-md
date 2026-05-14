package com.bizflow.common.reactive;

import java.util.concurrent.Callable;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

/**
 * WebFlux adapter for the current SQLite/JPA persistence layer.
 *
 * <p>SQLite JDBC and Spring Data JPA are blocking. Keeping the blocking calls behind this
 * boundary prevents controller code from accidentally occupying Netty event-loop threads
 * while still letting the domain services keep transactional semantics for the MVP.</p>
 */
@Component
public class BlockingJpaBridge {

    public <T> Mono<T> mono(Callable<T> blockingCall) {
        return Mono.fromCallable(blockingCall).subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<Void> run(CheckedRunnable blockingCall) {
        return Mono.fromRunnable(() -> {
            try {
                blockingCall.run();
            } catch (RuntimeException e) {
                throw e;
            } catch (Exception e) {
                throw new IllegalStateException(e);
            }
        }).subscribeOn(Schedulers.boundedElastic()).then();
    }

    public <T> Flux<T> flux(Callable<Iterable<T>> blockingCall) {
        return mono(blockingCall).flatMapMany(Flux::fromIterable);
    }

    @FunctionalInterface
    public interface CheckedRunnable {
        void run() throws Exception;
    }
}
