/**
 * ELARA — Alert Panel
 * Displays active psychological alerts with severity indicators.
 */

import React from "react";

const severityConfig = {
  CRITICAL  : { color: "#ff2244", bg: "#2a0a0f", border: "#ff2244" },
  HIGH      : { color: "#ff8800", bg: "#2a1500", border: "#ff8800" },
  MONITOR   : { color: "#ffcc00", bg: "#2a2000", border: "#ffcc00" },
  AT_RISK   : { color: "#ff8800", bg: "#2a1500", border: "#ff8800" },
};

export default function AlertPanel({ alerts = [] }) {
  if (!alerts || alerts.length === 0) {
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
        ✓ No active alerts. Psychological indicators nominal.
      </div>
    );
  }

  return (
    <div>
      {alerts.map((alert, idx) => {
        const config = severityConfig[alert.severity] || severityConfig["MONITOR"];
        return (
          <div key={idx} style={{
            background    : config.bg,
            border        : `1px solid ${config.border}`,
            borderRadius  : "8px",
            padding       : "12px 16px",
            marginBottom  : "8px",
          }}>
            <div style={{
              display       : "flex",
              alignItems    : "center",
              gap           : "8px",
              marginBottom  : "4px",
            }}>
              <span style={{
                background    : config.color,
                color         : "#000",
                fontSize      : "10px",
                fontWeight    : "bold",
                padding       : "2px 8px",
                borderRadius  : "4px",
                fontFamily    : "monospace",
              }}>
                {alert.severity}
              </span>
              <span style={{ color: config.color, fontSize: "12px", fontFamily: "monospace" }}>
                {alert.type}
              </span>
            </div>
            <p style={{ color: "#c0cce0", fontSize: "12px", margin: 0, fontFamily: "monospace" }}>
              {alert.message}
            </p>
          </div>
        );
      })}
    </div>
  );
}