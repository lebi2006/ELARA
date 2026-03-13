import React, { useState, useEffect, useRef, useCallback } from "react";
import api                  from "../services/api";
import CrewOverview         from "../components/CrewOverview";
import HealthIndexGauge     from "../components/HealthIndexGauge";
import SignalScoreCard      from "../components/SignalScoreCard";
import AlertPanel           from "../components/AlertPanel";
import TimelineChart        from "../components/TimelineChart";
import InterventionPanel    from "../components/InterventionPanel";

const MISSION_TOTAL = 180;

export default function Dashboard() {
  const [missionDay, setMissionDay]         = useState(60);
  const [displayDay, setDisplayDay]         = useState(60);
  const [crew, setCrew]                     = useState([]);
  const [selectedId, setSelectedId]         = useState("GAGANYAAN_01");
  const [selectedData, setSelectedData]     = useState(null);
  const [timeline, setTimeline]             = useState([]);
  const [interventions, setInterventions]   = useState(null);
  const [loading, setLoading]               = useState(true);
  const [simulating, setSimulating]         = useState(false);
  const debounceRef                         = useRef(null);
  const simRef                              = useRef(false);

  const fetchAll = useCallback(async (day, astronautId) => {
    try {
      const [crewData, interventionData] = await Promise.all([
        api.getCrewAssessment(day),
        api.getInterventions(astronautId, day),
      ]);
      setCrew(crewData.crew || []);
      const selected = (crewData.crew || []).find(c => c.astronaut_id === astronautId);
      if (selected) setSelectedData(selected);
      setInterventions(interventionData);
    } catch (err) {
      console.error("Fetch error:", err);
    }
  }, []);

  const fetchTimeline = useCallback(async (astronautId) => {
    try {
      const data = await api.getMissionTimeline(astronautId);
      setTimeline(data.map(d => ({ ...d, tqs_probability: d.tqs_probability * 100 })));
    } catch (err) {
      console.error("Timeline error:", err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([
        fetchAll(missionDay, selectedId),
        fetchTimeline(selectedId),
      ]);
      setLoading(false);
    };
    init();
  // eslint-disable-next-line
  }, []);

  // When astronaut changes
  useEffect(() => {
    if (loading) return;
    fetchAll(missionDay, selectedId);
    fetchTimeline(selectedId);
  // eslint-disable-next-line
  }, [selectedId]);

  // Slider handler — update display instantly, debounce fetch
  const handleSliderChange = (value) => {
    setDisplayDay(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setMissionDay(value);
      fetchAll(value, selectedId);
    }, 300);
  };

  // Simulation — smooth animation, fetch only at end
  const runSimulation = async () => {
    if (simulating) return;
    setSimulating(true);
    simRef.current = true;

    for (let day = 1; day <= MISSION_TOTAL; day++) {
      if (!simRef.current) break;
      setDisplayDay(day);
      await new Promise(r => setTimeout(r, 30));
    }

    // Fetch final result at Day 137
    setDisplayDay(137);
    setMissionDay(137);
    await fetchAll(137, selectedId);
    setSimulating(false);
    simRef.current = false;
  };

  const stopSimulation = () => {
    simRef.current = false;
    setSimulating(false);
  };

  const getMissionPhase = (day) => {
    if (day <= 14)  return { label: "BASELINE CALIBRATION",   color: "#00aaff" };
    if (day <= 60)  return { label: "OPERATIONAL STABLE",     color: "#00ff88" };
    if (day <= 119) return { label: "MID-MISSION FATIGUE",    color: "#ffcc00" };
    if (day <= 150) return { label: "THIRD-QUARTER SYNDROME", color: "#ff2244" };
    return            { label: "RETURN ANTICIPATION",         color: "#aa88ff" };
  };

  const phase = getMissionPhase(displayDay);

  if (loading) {
    return (
      <div style={{
        background      : "#060d18",
        minHeight       : "100vh",
        display         : "flex",
        flexDirection   : "column",
        alignItems      : "center",
        justifyContent  : "center",
        color           : "#00ff88",
        fontFamily      : "monospace",
        gap             : "16px",
      }}>
        <div style={{ fontSize: "28px", letterSpacing: "4px" }}>◈ ELARA</div>
        <div style={{ fontSize: "13px", color: "#8892aa" }}>Initializing mission systems...</div>
        <div style={{
          width           : "200px",
          height          : "2px",
          background      : "#1a2035",
          borderRadius    : "2px",
          overflow        : "hidden",
        }}>
          <div style={{
            width       : "40%",
            height      : "100%",
            background  : "#00ff88",
            animation   : "slide 1.2s infinite",
          }} />
        </div>
        <style>{`
          @keyframes slide {
            0%   { transform: translateX(-100%) }
            100% { transform: translateX(350%) }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{ background: "#060d18", minHeight: "100vh", color: "#e0eaff", fontFamily: "monospace" }}>

      {/* ── Header ─────────────────────────────────────────── */}
      <div style={{
        background      : "#0a1628",
        borderBottom    : "1px solid #1e2d40",
        padding         : "16px 32px",
        display         : "flex",
        justifyContent  : "space-between",
        alignItems      : "center",
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "20px", color: "#00aaff", letterSpacing: "3px" }}>
            ◈ ELARA
          </h1>
          <p style={{ margin: 0, fontSize: "11px", color: "#8892aa" }}>
            Silent Intelligence for Astronaut Psychological Resilience
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "32px" }}>
          <div style={{ textAlign: "center" }}>
            <p style={{ margin: 0, fontSize: "10px", color: "#8892aa" }}>MISSION PHASE</p>
            <p style={{ margin: 0, fontSize: "12px", color: phase.color, fontWeight: "bold" }}>
              {phase.label}
            </p>
          </div>
          <div style={{ textAlign: "right" }}>
            <p style={{ margin: 0, fontSize: "10px", color: "#8892aa" }}>MISSION DAY</p>
            <p style={{ margin: 0, fontSize: "36px", color: "#00aaff", fontWeight: "bold", lineHeight: 1 }}>
              {String(displayDay).padStart(3, "0")}
            </p>
          </div>
          <div style={{ textAlign: "right" }}>
            <p style={{ margin: 0, fontSize: "10px", color: "#8892aa" }}>PROGRESS</p>
            <p style={{ margin: 0, fontSize: "16px", color: "#ffcc00", fontWeight: "bold" }}>
              {Math.round((displayDay / MISSION_TOTAL) * 100)}%
            </p>
          </div>
        </div>
      </div>

      <div style={{ padding: "24px 32px" }}>

        {/* ── Mission Day Control ─────────────────────────── */}
        <div style={{
          background    : "#0d1b2a",
          border        : "1px solid #1e2d40",
          borderRadius  : "12px",
          padding       : "20px 24px",
          marginBottom  : "24px",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "14px" }}>
            <span style={{ color: "#8892aa", fontSize: "12px" }}>MISSION TIMELINE CONTROL</span>
            <div style={{ display: "flex", gap: "10px" }}>
              <button
                onClick={simulating ? stopSimulation : runSimulation}
                style={{
                  background    : simulating ? "#2a0a0f" : "#00aaff22",
                  border        : `1px solid ${simulating ? "#ff2244" : "#00aaff"}`,
                  color         : simulating ? "#ff2244" : "#00aaff",
                  padding       : "6px 18px",
                  borderRadius  : "6px",
                  cursor        : "pointer",
                  fontSize      : "12px",
                  fontFamily    : "monospace",
                }}
              >
                {simulating ? "■ STOP" : "▶ RUN DEMO SIMULATION"}
              </button>
            </div>
          </div>

          {/* Slider */}
          <input
            type="range" min="1" max={MISSION_TOTAL}
            value={displayDay}
            onChange={e => handleSliderChange(Number(e.target.value))}
            style={{ width: "100%", accentColor: "#00aaff", cursor: "pointer" }}
          />

          {/* Phase markers */}
          <div style={{
            display         : "grid",
            gridTemplateColumns: "14fr 46fr 59fr 30fr 30fr",
            fontSize        : "9px",
            marginTop       : "6px",
            textAlign       : "center",
          }}>
            <span style={{ color: "#00aaff" }}>BASELINE</span>
            <span style={{ color: "#00ff88" }}>OPERATIONAL</span>
            <span style={{ color: "#ffcc00" }}>MID-MISSION</span>
            <span style={{ color: "#ff2244" }}>⚠ TQS</span>
            <span style={{ color: "#aa88ff" }}>RETURN</span>
          </div>
        </div>

        {/* ── Crew Overview ───────────────────────────────── */}
        <div style={{ marginBottom: "24px" }}>
          <p style={{ color: "#8892aa", fontSize: "11px", marginBottom: "12px", letterSpacing: "1px" }}>
            CREW PSYCHOLOGICAL STATUS — SELECT ASTRONAUT FOR DETAIL
          </p>
          <CrewOverview
            crew={crew}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>

        {selectedData && (
          <>
            {/* ── Detail Row ──────────────────────────────── */}
            <div style={{
              display             : "grid",
              gridTemplateColumns : "1fr 1fr 1fr",
              gap                 : "20px",
              marginBottom        : "24px",
            }}>

              {/* Health Overview */}
              <div style={{
                background    : "#0d1b2a",
                border        : "1px solid #1e2d40",
                borderRadius  : "12px",
                padding       : "20px",
              }}>
                <p style={{ color: "#8892aa", fontSize: "11px", margin: "0 0 16px", letterSpacing: "1px" }}>
                  UNIFIED HEALTH INDEX — {selectedData.astronaut_name}
                </p>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: "16px" }}>
                  <HealthIndexGauge score={selectedData.health_index} size={180} />
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
                  <div style={{ textAlign: "center" }}>
                    <p style={{ color: "#8892aa", margin: "0 0 4px", fontSize: "10px" }}>COGNITIVE LOAD</p>
                    <p style={{ color: "#ff8800", fontWeight: "bold", margin: 0, fontSize: "22px" }}>
                      {Math.round(selectedData.cognitive_load_score)}
                    </p>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <p style={{ color: "#8892aa", margin: "0 0 4px", fontSize: "10px" }}>READINESS</p>
                    <p style={{ color: "#00ff88", fontWeight: "bold", margin: 0, fontSize: "22px" }}>
                      {Math.round(selectedData.cognitive_readiness_score)}
                    </p>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <p style={{ color: "#8892aa", margin: "0 0 4px", fontSize: "10px" }}>RISK LEVEL</p>
                    <p style={{ color: "#ffcc00", fontWeight: "bold", margin: 0, fontSize: "14px" }}>
                      {selectedData.risk_level}
                    </p>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <p style={{ color: "#8892aa", margin: "0 0 4px", fontSize: "10px" }}>TQS PROBABILITY</p>
                    <p style={{ color: "#ff2244", fontWeight: "bold", margin: 0, fontSize: "14px" }}>
                      {Math.round(selectedData.tqs_probability * 100)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Signal Scores */}
              <div style={{
                background    : "#0d1b2a",
                border        : "1px solid #1e2d40",
                borderRadius  : "12px",
                padding       : "20px",
              }}>
                <p style={{ color: "#8892aa", fontSize: "11px", margin: "0 0 16px", letterSpacing: "1px" }}>
                  BEHAVIORAL SIGNAL SCORES
                </p>
                <SignalScoreCard label="Voice Stress"      score={selectedData.signal_scores?.voice_stress}      icon="🎙" />
                <SignalScoreCard label="Sleep Disruption"  score={selectedData.signal_scores?.sleep_disruption}  icon="🌙" />
                <SignalScoreCard label="Cognitive Latency" score={selectedData.signal_scores?.cognitive_latency} icon="⚡" />
                <SignalScoreCard label="Linguistic Drift"  score={selectedData.signal_scores?.linguistic_drift}  icon="📝" />
              </div>

              {/* Alerts + Interventions */}
              <div style={{
                background    : "#0d1b2a",
                border        : "1px solid #1e2d40",
                borderRadius  : "12px",
                padding       : "20px",
                overflowY     : "auto",
                maxHeight     : "480px",
              }}>
                <p style={{ color: "#8892aa", fontSize: "11px", margin: "0 0 12px", letterSpacing: "1px" }}>
                  ACTIVE ALERTS
                </p>
                <AlertPanel alerts={selectedData.alerts} />
                <p style={{ color: "#8892aa", fontSize: "11px", margin: "16px 0 12px", letterSpacing: "1px" }}>
                  RECOMMENDED INTERVENTIONS
                </p>
                <InterventionPanel data={interventions} />
              </div>
            </div>

            {/* ── Timeline Chart ───────────────────────────── */}
            <div style={{
              background    : "#0d1b2a",
              border        : "1px solid #1e2d40",
              borderRadius  : "12px",
              padding       : "20px",
            }}>
              <p style={{ color: "#8892aa", fontSize: "11px", margin: "0 0 16px", letterSpacing: "1px" }}>
                180-DAY PSYCHOLOGICAL TRAJECTORY — {selectedData.astronaut_name}
                <span style={{ color: "#ff2244", marginLeft: "16px" }}>
                  ⚠ TQS DANGER ZONE: DAYS 120–150
                </span>
              </p>
              <TimelineChart data={timeline} currentDay={displayDay} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}