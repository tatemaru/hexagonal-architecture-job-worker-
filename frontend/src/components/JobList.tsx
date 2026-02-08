import type { Job } from "../api/jobApi";
import { JobStatusBadge } from "./JobStatusBadge";

interface Props {
  jobs: Job[];
  onCancel: (jobId: string) => void;
}

const CANCELLABLE = new Set(["PENDING", "RUNNING"]);

export function JobList({ jobs, onCancel }: Props) {
  if (jobs.length === 0) {
    return <p>ジョブがありません</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th style={th}>ID</th>
          <th style={th}>ステータス</th>
          <th style={th}>秒数</th>
          <th style={th}>通知</th>
          <th style={th}>作成日時</th>
          <th style={th}>操作</th>
        </tr>
      </thead>
      <tbody>
        {jobs.map((job) => (
          <tr key={job.id}>
            <td style={td}>{job.id.slice(0, 8)}</td>
            <td style={td}>
              <JobStatusBadge status={job.status} />
            </td>
            <td style={td}>{job.duration_seconds}s</td>
            <td style={td}>{job.notification_channel}</td>
            <td style={td}>{new Date(job.created_at).toLocaleString()}</td>
            <td style={td}>
              {CANCELLABLE.has(job.status) && (
                <button onClick={() => onCancel(job.id)}>キャンセル</button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const th: React.CSSProperties = {
  textAlign: "left",
  borderBottom: "2px solid #ccc",
  padding: "8px",
};

const td: React.CSSProperties = {
  borderBottom: "1px solid #eee",
  padding: "8px",
};
