# SentinelMind Frontend

React-based tactical command center for real-time disaster response monitoring.

## Technical Stack

- **Framework**: React + Vite
- **Styling**: Tailwind CSS
- **Backend**: Firebase Firestore with native `onSnapshot()` listeners
- **Auth**: Custom JWT-based proxy mode + Firebase Auth fallback

## Key Features

- Real-time emergency dashboard with tactical map visualization
- Hybrid authentication (proxy mode for service-account.json, Firebase Auth fallback)
- Live Firestore subscriptions for instant state updates
- Field image upload with AI vision analysis
- Asset/resource tree management

## Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create `.env`:
```bash
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_PROJECT_ID=your_project_id
```

## Architecture

| Component | Purpose |
|-----------|---------|
| `src/pages/Dashboard.jsx` | Real-time emergency monitoring |
| `src/pages/AssetTree.jsx` | Resource/vehicle management |
| `src/pages/FieldUpload.jsx` | AI-powered image analysis |
| `src/context/AuthContext.jsx` | Authentication state |