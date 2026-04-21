# SentinelMind: Multi-Agent Autonomous Disaster Response

## Mission
To dramatically decrease the emergency response time window from hours to seconds by leveraging a swarm of Gemini-powered autonomous agents integrated with Google Cloud Services (Vertex AI, Maps, Firestore).

## Project Structure
- `backend/`: Python-based logic for triage ingestion, resource management, and meta-orchestration.
- `frontend/`: React-based Enterprise Command Center dashboard.
- `scripts/`: Operational scripts, daemons (Watcher, Discord Actuator), and stress-testing tools.
- `Archives/`: Documentation, roadmaps, and technical specifications.

## Technology Stack
- **Cloud**: Google Cloud Platform (Vertex AI, Secret Manager, Cloud Run).
- **Database**: Firebase Firestore.
- **Frontend**: React, Tailwind CSS, Google Maps React API, Firebase Hosting.
- **AI/ML**: Gemini 1.5 Flash (Triage), Gemini 1.5 Pro (RAG & Risk Assessment), Gemini 1.5 Pro Vision (Image Analysis).
- **Logistics**: Google Maps Routes API.
- **Actuation**: Discord Webhook API.

## Team Roles
- **Role 1**: System Designer & Meta-Orchestrator (The Brain).
- **Role 2**: Triage Ingestion Lead (The Filter).
- **Role 3**: Logistics & Prediction Lead (The Muscle).
- **Role 4**: UI/UX & Communication Lead (The Glass).

## Getting Started
Refer to `Archives/ROADMAP.md` for the day-by-day implementation strategy.
See `Archives/schema.json` for the data contract between agents.
