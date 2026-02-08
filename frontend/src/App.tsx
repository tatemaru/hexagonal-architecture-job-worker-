import { useCallback, useEffect, useState } from "react";
import { type Job, cancelJob, createJob, listJobs } from "./api/jobApi";
import { JobCreateForm } from "./components/JobCreateForm";
import { JobList } from "./components/JobList";
import { type JobEvent, useJobSSE } from "./hooks/useJobSSE";

const EVENT_TO_STATUS: Record<string, string> = {
  JobCreated: "PENDING",
  JobStarted: "RUNNING",
  JobCompleted: "COMPLETED",
  JobFailed: "FAILED",
  JobCancelled: "CANCELLED",
};

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);

  const reload = useCallback(async () => {
    setJobs(await listJobs());
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  useJobSSE((event: JobEvent) => {
    const newStatus = EVENT_TO_STATUS[event.event_type];
    if (!newStatus) return;

    setJobs((prev) => {
      const exists = prev.some((j) => j.id === event.job_id);
      if (!exists) {
        // 新しいジョブ（JobCreated）の場合、リロードして取得
        reload();
        return prev;
      }
      return prev.map((j) =>
        j.id === event.job_id ? { ...j, status: newStatus } : j,
      );
    });
  });

  const handleCreate = async (
    durationSeconds: number,
    notificationChannel: string,
  ) => {
    await createJob(durationSeconds, notificationChannel);
    await reload();
  };

  const handleCancel = async (jobId: string) => {
    await cancelJob(jobId);
    await reload();
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "24px" }}>
      <h1>Job Worker</h1>
      <JobCreateForm onSubmit={handleCreate} />
      <JobList jobs={jobs} onCancel={handleCancel} />
    </div>
  );
}

export default App;
