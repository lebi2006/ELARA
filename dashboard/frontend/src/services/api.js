/**
 * ELARA — API Service
 * Connects React frontend to FastAPI backend.
 */

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = {

  // ── Assessment ────────────────────────────────────────────
  getCrewAssessment: async (missionDay) => {
    const res = await fetch(`${BASE_URL}/api/assessment/crew/${missionDay}`);
    return res.json();
  },

  getAstronautAssessment: async (astronautId, missionDay) => {
    const res = await fetch(`${BASE_URL}/api/assessment/${astronautId}/${missionDay}`);
    return res.json();
  },

  getCrewInfo: async () => {
    const res = await fetch(`${BASE_URL}/api/assessment/crew/info/all`);
    return res.json();
  },

  // ── Mission ───────────────────────────────────────────────
  getMissionTimeline: async (astronautId) => {
    const res = await fetch(`${BASE_URL}/api/mission/timeline/${astronautId}`);
    return res.json();
  },

  // ── Interventions ─────────────────────────────────────────
  getInterventions: async (astronautId, missionDay) => {
    const res = await fetch(`${BASE_URL}/api/intervention/${astronautId}/${missionDay}`);
    return res.json();
  },

  recordEffectiveness: async (astronautId, interventionId, effectiveness) => {
    const res = await fetch(`${BASE_URL}/api/intervention/effectiveness`, {
      method  : "POST",
      headers : { "Content-Type": "application/json" },
      body    : JSON.stringify({ astronaut_id: astronautId, intervention_id: interventionId, effectiveness }),
    });
    return res.json();
  },
};

export default api;