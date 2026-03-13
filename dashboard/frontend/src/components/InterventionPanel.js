/**
 * ELARA — Intervention Panel
 * Displays recommended micro-interventions.
 */

import React from "react";

const typeColors = {
  BREATHING           : "#00aaff",
  REST                : "#00ff88",
  SOCIAL_CONNECTION   : "#aa88ff",
  COGNITIVE_REFRAME   : "#ffcc00",
  MUSIC_THERAPY       : "#ff88aa",
  EMERGENCY_PROTOCOL  : "#ff2244",
  MISSION_CONTROL_ALERT: "#ff8800",
  PROFESSIONAL_SUPPORT: "#ff8800",
  RECOGNITION         : "#00ff88",
  FUTURE_FOCUS        : "#00aaff",
  AUTONOMY_RESTORATION: "#aa88ff",
  ENVIRONMENT         : "#00ff88",
  RELAXATION          : "#00aaff",
  CREW_SUPPORT        : "#aa88ff",
};

export default function InterventionPanel({ data }) {
  if (!data || data.status === "NO_INTERVENTION_NEEDED") {
    return (
      <div style={{
        background    : "#0a1f0a",
        border        : "1px solid #1a4a1a",
        borderRadius  : "10px",
        padding       : "16px",
        color         : "#00ff88",
        fontFamily    : "monospace",
        fontSize      : "13px",
      }}>
        ✓ No interventions required today.
      </div>
    );
  }

  return (
    <div>
      {(data.interventions || []).map((item, idx) => {
        const iv    = item.intervention;
        const color = typeColors[iv.type] || "#8892aa";
        return (
          <div key={idx} style={{
            background    : "#0d1b2a",
            border        : `1px solid ${color}33`,
            borderRadius  : "10px",
            padding       : "14px 16px",
            marginBottom  : "10px",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
              <span style={{ color, fontWeight: "bold", fontSize: "13px", fontFamily: "monospace" }}>
                {iv.title}
              </span>
              <span style={{
                background  : `${color}22`,
                color,
                fontSize    : "10px",
                padding     : "2px 8px",
                borderRadius: "4px",
                fontFamily  : "monospace",
              }}>
                {iv.type}
              </span>
            </div>
            <p style={{ color: "#c0cce0", fontSize: "12px", margin: "0 0 6px", fontFamily: "monospace" }}>
              {iv.description}
            </p>
            <div style={{ display: "flex", gap: "12px" }}>
              <span style={{ color: "#8892aa", fontSize: "11px", fontFamily: "monospace" }}>
                ⏱ {iv.duration_min > 0 ? `${iv.duration_min} min` : "Immediate"}
              </span>
              <span style={{ color: "#8892aa", fontSize: "11px", fontFamily: "monospace" }}>
                📡 {iv.delivery}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}