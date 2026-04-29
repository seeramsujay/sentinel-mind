# Sentinel-Mind: Live Demo Script

## 1. Introduction (0:00 - 0:30)
**Speaker:** "Welcome to Sentinel-Mind, an AI-driven, real-time emergency management and logistics orchestration platform. During a crisis, seconds matter. Sentinel-Mind ingests live data, coordinates rescue assets autonomously, and most importantly, resolves the duplicate distress signal issue highlighted by recent NDMA post-mortem reports. Let's see it in action."
## 2. Accessing the Platform (0:30 - 1:00)
**Action:** Open the browser and navigate to the live deployment URL.
**Speaker:** "Our frontend is lightning-fast and globally distributed via Firebase Hosting, while our heavy-duty AI processing and Meta-Orchestrator run securely on the backend. As we log in, we are greeted by the Global Tactical Grid."
## 3. The Global Tactical Grid (1:00 - 1:45)
**Action:** Pan and zoom around the Google Map interface in the center panel.
**Speaker:** "At the core is our interactive tactical grid, powered by Google Maps. Here, you can see live incidents pulsing on the map. 
- **Red indicators** represent Critical P1 emergencies.
- **Blue indicators** represent Routine or P2 events.
The UI is designed to be glassmorphic and distraction-free, ensuring commanders focus strictly on mission-critical data."
## 4. Real-Time Agent Feed & Deduplication (1:45 - 2:30)
**Action:** Point to the left sidebar (Agent Feed). Select overlapping incidents.
**Speaker:** "On the left, we have our live Agent Feed. This is where our Meta-Orchestrator shines. During disasters, panic causes hundreds of duplicate SOS calls for the same event, causing resource conflicts. Sentinel-Mind autonomously clusters these signals, identifies duplicates, and resolves the resource conflict before dispatching assets—preventing critical bottlenecks."
## 5. Multimodal Drone Intelligence (2:30 - 3:15)
**Action:** Click the 'UPLOAD FIELD IMAGE' button on the bottom Command Bar and simulate uploading a drone image.
**Speaker:** "For rapid situational awareness, we rely on multimodal AI. Here, field units or drones upload damage imagery. We use the Gemini 2.5 Flash Multimodal model to instantly scan the image, categorize damage severity, and identify trapped civilians or structural failures—translating pixels into actionable logistics data."
## 6. Transparency-as-a-Service (3:15 - 4:00)
**Action:** Direct attention to the right sidebar. Expand the 'System Audit Log' (arrow icon) on the selected incident.
**Speaker:** "With AI making critical dispatch decisions, trust is paramount. On the right, we have our Transparency-as-a-Service Panel—also serving as our Fairness Audit Feed. It eliminates the black-box problem. By expanding these logs, commanders see the exact logic, confidence scores, and NDMA protocols the AI used to make its decisions."
## 7. Conclusion (4:00 - 4:30)
**Speaker:** "In summary, Sentinel-Mind combines Firebase Hosting, Gemini 2.5 Multimodal intelligence, and real-time mapping to turn chaotic duplicate signals into coordinated, transparent, life-saving action. Thank you."
