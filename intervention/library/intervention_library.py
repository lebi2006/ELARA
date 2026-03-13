"""
ELARA — Intervention Library
Curated database of micro-interventions for astronaut psychological support.
Each intervention is mapped to specific risk conditions and astronaut profiles.
Based on NASA Human Research Program and ESA psychological support protocols.
"""

# Complete intervention library
# Structure: condition -> list of interventions
INTERVENTION_LIBRARY = {

    "COGNITIVE_OVERLOAD": [
        {
            "id"            : "COG_001",
            "title"         : "4-7-8 Breathing Protocol",
            "description"   : "Inhale for 4 counts, hold for 7, exhale for 8. Repeat 4 cycles.",
            "duration_min"  : 4,
            "type"          : "BREATHING",
            "evidence"      : "Activates parasympathetic nervous system. Reduces cortisol within 4 minutes.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "COG_002",
            "title"         : "Cognitive Offload Break",
            "description"   : "Step away from all screens for 10 minutes. No tasks. No communication.",
            "duration_min"  : 10,
            "type"          : "REST",
            "evidence"      : "Prefrontal cortex recovery requires unstructured downtime.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "COG_003",
            "title"         : "Pre-Task Readiness Check",
            "description"   : "Mission Control notified: recommend delaying EVA or critical repair by 4 hours.",
            "duration_min"  : 0,
            "type"          : "MISSION_CONTROL_ALERT",
            "evidence"      : "NASA protocol: no high-risk tasks below cognitive readiness threshold 40.",
            "delivery"      : "MISSION_CONTROL",
        },
    ],

    "PSYCHOLOGICAL_DRIFT": [
        {
            "id"            : "DRIFT_001",
            "title"         : "Family Connection Window",
            "description"   : "A personal message from your family has been queued. Available when ready.",
            "duration_min"  : 15,
            "type"          : "SOCIAL_CONNECTION",
            "evidence"      : "Social bonds are the strongest protective factor against isolation-induced drift.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "DRIFT_002",
            "title"         : "Mission Progress Reflection",
            "description"   : "You are {mission_day} days into a {total_days}-day mission. Review your personal mission milestones.",
            "duration_min"  : 10,
            "type"          : "COGNITIVE_REFRAME",
            "evidence"      : "Progress visualization combats third-quarter motivational collapse.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "DRIFT_003",
            "title"         : "Unstructured Creative Time",
            "description"   : "30 minutes of personal time added to tomorrow's schedule. No mission objectives.",
            "duration_min"  : 30,
            "type"          : "AUTONOMY_RESTORATION",
            "evidence"      : "Autonomy is a primary psychological need. Restoration reduces drift markers.",
            "delivery"      : "SCHEDULE",
        },
        {
            "id"            : "DRIFT_004",
            "title"         : "Psychological Support Session",
            "description"   : "Flight psychologist has been notified. Optional video consultation available.",
            "duration_min"  : 45,
            "type"          : "PROFESSIONAL_SUPPORT",
            "evidence"      : "Early professional intervention prevents escalation to crisis level.",
            "delivery"      : "MISSION_CONTROL",
        },
    ],

    "SLEEP_DISRUPTION": [
        {
            "id"            : "SLEEP_001",
            "title"         : "Sleep Hygiene Protocol",
            "description"   : "Dim cabin lighting 1 hour before sleep. Avoid screens. Cabin temperature adjusted.",
            "duration_min"  : 60,
            "type"          : "ENVIRONMENT",
            "evidence"      : "Light exposure is the primary circadian regulator in microgravity.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "SLEEP_002",
            "title"         : "Body Scan Relaxation",
            "description"   : "12-minute guided progressive muscle relaxation. Audio queued in your interface.",
            "duration_min"  : 12,
            "type"          : "RELAXATION",
            "evidence"      : "Reduces sleep onset latency by average 18 minutes in isolation studies.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "SLEEP_003",
            "title"         : "Recovery Rest Block",
            "description"   : "20-minute scheduled rest block added to afternoon schedule.",
            "duration_min"  : 20,
            "type"          : "REST",
            "evidence"      : "Strategic napping restores cognitive performance during chronic sleep deficit.",
            "delivery"      : "SCHEDULE",
        },
    ],

    "TQS_PREVENTION": [
        {
            "id"            : "TQS_001",
            "title"         : "Milestone Celebration Protocol",
            "description"   : "Mission Control message: You have completed 75% of your mission. Special acknowledgment from ISRO ground team.",
            "duration_min"  : 5,
            "type"          : "RECOGNITION",
            "evidence"      : "External validation from mission authority is a documented TQS protective factor.",
            "delivery"      : "BOTH",
        },
        {
            "id"            : "TQS_002",
            "title"         : "Return Countdown Activation",
            "description"   : "Homecoming countdown now visible on your interface. Days remaining: {days_remaining}.",
            "duration_min"  : 0,
            "type"          : "FUTURE_FOCUS",
            "evidence"      : "Concrete return timeline visualization reduces TQS severity significantly.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
        {
            "id"            : "TQS_003",
            "title"         : "Preferred Music Therapy",
            "description"   : "Your personal playlist has been queued. 20 minutes of selected music.",
            "duration_min"  : 20,
            "type"          : "MUSIC_THERAPY",
            "evidence"      : "Personally meaningful music activates reward pathways suppressed during TQS.",
            "delivery"      : "ASTRONAUT_INTERFACE",
        },
    ],

    "CRITICAL_ALERT": [
        {
            "id"            : "CRIT_001",
            "title"         : "Immediate Flight Surgeon Review",
            "description"   : "Flight surgeon has been automatically notified. Priority psychological review scheduled.",
            "duration_min"  : 0,
            "type"          : "EMERGENCY_PROTOCOL",
            "evidence"      : "NASA HFBP protocol: automatic escalation at health index below 25.",
            "delivery"      : "MISSION_CONTROL",
        },
        {
            "id"            : "CRIT_002",
            "title"         : "Crew Support Activation",
            "description"   : "Peer support protocol activated. Crew members briefed to provide social support.",
            "duration_min"  : 0,
            "type"          : "CREW_SUPPORT",
            "evidence"      : "Peer support is the most accessible and effective crisis intervention in space.",
            "delivery"      : "MISSION_CONTROL",
        },
    ],
}


def get_interventions_for_condition(condition: str) -> list:
    return INTERVENTION_LIBRARY.get(condition, [])


def get_intervention_by_id(intervention_id: str) -> dict:
    for interventions in INTERVENTION_LIBRARY.values():
        for intervention in interventions:
            if intervention["id"] == intervention_id:
                return intervention
    return {}