/**
 * ELARA — Mission Timeline Chart
 * 180-day psychological health trajectory visualization.
 */

import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Legend
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background  : "#0d1b2a",
        border      : "1px solid #1e2d40",
        borderRadius: "8px",
        padding     : "12px",
        fontFamily  : "monospace",
        fontSize    : "12px",
      }}>
        <p style={{ color: "#8892aa", margin: "0 0 6px" }}>Day {label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color, margin: "2px 0" }}>
            {p.name}: {Math.round(p.value)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function TimelineChart({ data = [], currentDay = 1 }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1a2035" />
        <XAxis
          dataKey="mission_day"
          stroke="#3a4a5a"
          tick={{ fill: "#8892aa", fontSize: 11, fontFamily: "monospace" }}
          label={{ value: "Mission Day", position: "insideBottom", offset: -2, fill: "#8892aa", fontSize: 11 }}
        />
        <YAxis
          stroke="#3a4a5a"
          tick={{ fill: "#8892aa", fontSize: 11, fontFamily: "monospace" }}
          domain={[0, 100]}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontFamily: "monospace", fontSize: "12px", color: "#8892aa" }}
        />
        {/* TQS danger zone */}
        <ReferenceLine x={120} stroke="#ff2244" strokeDasharray="4 4" label={{ value: "TQS Start", fill: "#ff2244", fontSize: 10 }} />
        <ReferenceLine x={150} stroke="#ff8800" strokeDasharray="4 4" label={{ value: "TQS End", fill: "#ff8800", fontSize: 10 }} />
        {/* Current day */}
        <ReferenceLine x={currentDay} stroke="#00aaff" strokeWidth={2} label={{ value: "Today", fill: "#00aaff", fontSize: 10 }} />

        <Line
          type="monotone" dataKey="health_index"
          stroke="#00ff88" strokeWidth={2}
          dot={false} name="Health Index"
        />
        <Line
          type="monotone" dataKey="cognitive_load_score"
          stroke="#ff8800" strokeWidth={1.5}
          dot={false} name="Cognitive Load"
        />
        <Line
          type="monotone" dataKey="tqs_probability"
          stroke="#ff2244" strokeWidth={1.5}
          dot={false} name="TQS Risk"
          // Scale 0-1 to 0-100
          // handled via formatter below
        />
      </LineChart>
    </ResponsiveContainer>
  );
}