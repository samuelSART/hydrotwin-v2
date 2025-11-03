import { TypedEmitter } from "tiny-typed-emitter";

interface TimerEvents {
    tick: () => void;
}

interface TimerConfig {
    timeout: number;
    immediate: boolean;
}

class Timer extends TypedEmitter<TimerEvents> {
    private intervalId: number | null = null;
    private timerConfig!: TimerConfig;

    constructor(
        timerConfig: TimerConfig = { timeout: 1000, immediate: false }
    ) {
        super();

        this.timerConfig = timerConfig;
        this.intervalId = null;
    }

    start(): void {
        if (this.timerConfig.immediate) this.tick();

        this.intervalId = setInterval(() => {
            this.tick();
        }, this.timerConfig.timeout);
    }

    stop(): void {
        if (this.intervalId) clearInterval(this.intervalId);
    }

    reset(): void {
        this.stop();
        this.start();
    }

    tick(): void {
        this.emit("tick");
    }
}

export { Timer };
