import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export default function ValueChart({ collectionId, refreshKey }) {
  const [data, setData] = useState([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [collectionName, setCollectionName] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/collections/${collectionId}/value-history/?days=${days}`)
      .then((res) => res.json())
      .then((json) => {
        setCollectionName(json.collection_name || "");
        const formatted = (json.history || []).map((point) => ({
          date: point.date,
          value: parseFloat(point.total_value),
        }));
        setData(formatted);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [collectionId, days, refreshKey]);

  if (loading) return <p>Loading chart...</p>;

  return (
    <div style={{ width: "100%", padding: "20px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h3 style={{ margin: 0 }}>
          {collectionName} — Market Value ({days} Days)
        </h3>
        <div>
          <button
            onClick={() => setDays(30)}
            style={{
              padding: "6px 16px",
              marginRight: "8px",
              borderRadius: "6px",
              border: days === 30 ? "2px solid #4f46e5" : "1px solid #ccc",
              background: days === 30 ? "#eef2ff" : "#fff",
              cursor: "pointer",
            }}
          >
            30 Days
          </button>
          <button
            onClick={() => setDays(60)}
            style={{
              padding: "6px 16px",
              borderRadius: "6px",
              border: days === 60 ? "2px solid #4f46e5" : "1px solid #ccc",
              background: days === 60 ? "#eef2ff" : "#fff",
              cursor: "pointer",
            }}
          >
            60 Days
          </button>
        </div>
      </div>

      {data.length === 0 ? (
        <p>No value data recorded yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(d) => {
                const date = new Date(d + "T00:00:00");
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis
              tickFormatter={(v) => `$${v.toLocaleString()}`}
            />
            <Tooltip
              formatter={(v) => [`$${v.toLocaleString()}`, "Value"]}
              labelFormatter={(d) => {
                const date = new Date(d + "T00:00:00");
                return date.toLocaleDateString();
              }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#4f46e5"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}