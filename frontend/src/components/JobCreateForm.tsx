import { useState } from "react";

interface Props {
  onSubmit: (durationSeconds: number, notificationChannel: string) => void;
}

export function JobCreateForm({ onSubmit }: Props) {
  const [duration, setDuration] = useState("");
  const [notificationChannel, setNotificationChannel] = useState("none");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseInt(duration, 10);
    if (!duration || isNaN(value) || value <= 0) {
      setError("1以上の整数を入力してください");
      return;
    }
    setError("");
    onSubmit(value, notificationChannel);
    setDuration("");
    setNotificationChannel("none");
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "16px" }}>
      <label>
        実行秒数:{" "}
        <input
          type="number"
          min="1"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          style={{ width: "80px", marginRight: "8px" }}
        />
      </label>
      <label>
        通知:{" "}
        <select
          value={notificationChannel}
          onChange={(e) => setNotificationChannel(e.target.value)}
          style={{ marginRight: "8px" }}
        >
          <option value="none">なし</option>
          <option value="email">Email</option>
          <option value="discord">Discord</option>
        </select>
      </label>
      <button type="submit">作成</button>
      {error && (
        <span style={{ color: "red", marginLeft: "8px" }}>{error}</span>
      )}
    </form>
  );
}
