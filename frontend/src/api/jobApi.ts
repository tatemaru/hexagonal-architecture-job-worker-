export interface Job {
  id: string;
  status: string;
  duration_seconds: number;
  notification_channel: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  result_message: string | null;
  result_error: string | null;
}

const BASE = "/api/jobs";

export async function createJob(
  durationSeconds: number,
  notificationChannel: string = "none",
): Promise<Job> {
  const res = await fetch(BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      duration_seconds: durationSeconds,
      notification_channel: notificationChannel,
    }),
  });
  return res.json();
}

export async function listJobs(): Promise<Job[]> {
  const res = await fetch(BASE);
  return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await fetch(`${BASE}/${jobId}`);
  return res.json();
}

export async function cancelJob(jobId: string): Promise<Job> {
  const res = await fetch(`${BASE}/${jobId}/cancel`, { method: "POST" });
  return res.json();
}
