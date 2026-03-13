/**
 * ELARA — Health Index Gauge
 * Circular gauge showing unified psychological health score.
 */

import React from "react";

const getColor = (score) => {
  if (score >= 70) return "#00ff88";
  if (score >= 45) return "#ffcc00";
  if (score >= 25) return "#ff8800";
  return "#ff2244";
};

const getStatus = (score) => {
  if (score >= 70) return "STABLE";
  if (score >= 45) return "MONITOR";
  if (score >= 25) return "AT RISK";
  return "CRITICAL";
};

export default function HealthIndexGauge({ score = 0, size = 160 }) {
  const radius      = size / 2 - 16;
  const circumference = 2 * Math.PI * radius;
  const progress    = ((100 - score) / 100) * circumference;
  const color       = getColor(score);
  const status      = getStatus(score);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <svg width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="#1a2035" strokeWidth="10"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={progress}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
        {/* Score text */}
        <text
          x={size / 2} y={size / 2 - 6}
          textAnchor="middle" fill={color}
          fontSize={size / 5} fontWeight="bold"
          fontFamily="monospace"
        >
          {Math.round(score)}
        </text>
        {/* Status text */}
        <text
          x={size / 2} y={size / 2 + 16}
          textAnchor="middle" fill="#8892aa"
          fontSize={size / 12} fontFamily="monospace"
        >
          {status}
        </text>
      </svg>
    </div>
  );
}