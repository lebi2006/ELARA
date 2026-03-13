/**
 * ELARA — Signal Score Card
 * Displays individual behavioral signal scores.
 */

import React from "react";

const getBarColor = (score) => {
  if (score <= 30) return "#00ff88";
  if (score <= 60) return "#ffcc00";
  if (score <= 80) return "#ff8800";
  return "#ff2244";
};

export default function SignalScoreCard({ label, score = 0, icon }) {
  const color = getBarColor(score);

  return (
    <div style={{
      background    : "#0d1b2a",
      border        : "1px solid #1e2d40",
      borderRadius  : "10px",
      padding       : "14px 18px",
      marginBottom  : "10px",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
        <span style={{ color: "#8892aa", fontSize: "12px", fontFamily: "monospace" }}>
          {icon} {label}
        </span>
        <span style={{ color, fontSize: "14px", fontWeight: "bold", fontFamily: "monospace" }}>
          {Math.round(score)}
        </span>
      </div>
      {/* Progress bar */}
      <div style={{ background: "#1a2035", borderRadius: "4px", height: "6px" }}>
        <div style={{
          width         : `${Math.min(score, 100)}%`,
          background    : color,
          height        : "6px",
          borderRadius  : "4px",
          transition    : "width 0.8s ease",
        }} />
      </div>
    </div>
  );
}