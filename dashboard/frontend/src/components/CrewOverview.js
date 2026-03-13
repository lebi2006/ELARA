/**
 * ELARA — Crew Overview
 * Summary cards for all crew members.
 */

import React from "react";
import HealthIndexGauge from "./HealthIndexGauge";

const riskColors = {
  LOW       : "#00ff88",
  MODERATE  : "#ffcc00",
  HIGH      : "#ff8800",
  CRITICAL  : "#ff2244",
};

export default function CrewOverview({ crew = [], selectedId, onSelect }) {
  return (
    <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
      {crew.map((member) => {
        const isSelected  = member.astronaut_id === selectedId;
        const riskColor   = riskColors[member.risk_level] || "#8892aa";

        return (
          <div
            key={member.astronaut_id}
            onClick={() => onSelect(member.astronaut_id)}
            style={{
              background    : isSelected ? "#0d2040" : "#0d1b2a",
              border        : `2px solid ${isSelected ? "#00aaff" : "#1e2d40"}`,
              borderRadius  : "12px",
              padding       : "20px",
              cursor        : "pointer",
              minWidth      : "200px",
              flex          : 1,
              transition    : "all 0.2s ease",
            }}
          >
            <HealthIndexGauge score={member.health_index} size={120} />
            <div style={{ textAlign: "center", marginTop: "12px" }}>
              <p style={{
                color       : "#e0eaff",
                fontWeight  : "bold",
                fontFamily  : "monospace",
                fontSize    : "14px",
                margin      : "0 0 4px",
              }}>
                {member.astronaut_name}
              </p>
              <p style={{ color: "#8892aa", fontSize: "11px", fontFamily: "monospace", margin: "0 0 8px" }}>
                {member.astronaut_id}
              </p>
              <span style={{
                background  : `${riskColor}22`,
                color       : riskColor,
                fontSize    : "11px",
                padding     : "3px 10px",
                borderRadius: "12px",
                fontFamily  : "monospace",
              }}>
                {member.risk_level}
              </span>
              {member.alerts && member.alerts.length > 0 && (
                <p style={{ color: "#ff2244", fontSize: "11px", fontFamily: "monospace", margin: "8px 0 0" }}>
                  ⚠ {member.alerts.length} alert{member.alerts.length > 1 ? "s" : ""}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}