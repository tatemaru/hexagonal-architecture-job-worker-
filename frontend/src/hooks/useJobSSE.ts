import { useEffect, useRef } from "react";

export interface JobEvent {
  event_type: string;
  job_id: string;
  status?: string;
  timestamp: string;
}

export function useJobSSE(onEvent: (event: JobEvent) => void) {
  const callbackRef = useRef(onEvent);
  callbackRef.current = onEvent;

  useEffect(() => {
    const source = new EventSource("/api/jobs/stream");

    const eventTypes = [
      "JobCreated",
      "JobStarted",
      "JobCompleted",
      "JobFailed",
      "JobCancelled",
    ];

    for (const type of eventTypes) {
      source.addEventListener(type, (e: MessageEvent) => {
        const data: JobEvent = JSON.parse(e.data);
        callbackRef.current(data);
      });
    }

    source.onerror = () => {
      console.log("SSE connection error, will auto-reconnect");
    };

    return () => {
      source.close();
    };
  }, []);
}
