const STATUS_COLORS: Record<string, string> = {
  PENDING: "#6b7280",
  RUNNING: "#3b82f6",
  COMPLETED: "#22c55e",
  FAILED: "#ef4444",
  CANCELLED: "#eab308",
};

export function JobStatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] ?? "#6b7280";
  return (
    <span
      style={{
        backgroundColor: color,
        color: "#fff",
        padding: "2px 8px",
        borderRadius: "4px",
        fontSize: "12px",
        fontWeight: "bold",
      }}
    >
      {status}
    </span>
  );
}
