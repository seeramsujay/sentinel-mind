Here is exactly what everyone must do, day by day, to pull this off.

### The Absolute Prerequisite: April 21 Evening - Phase 0 (COMPLETED)
Before anyone codes, the team must finalize the JSON Schema and state pipeline. Ensure the new keys (`carbon_saved`, `language_preference`, `awaiting_human_approval`, `fairness_audit`) are locked in. 
- [x] Repository Initialized.
- [x] Initial Context Artifacts Created.
- [x] JSON Schema (`Archives/schema.json`) Finalized.
- [x] Project Scaffolding (Frontend/Backend) Done.
- [x] Gitignore configured.

---

### Role 1: Meta-Orchestrator & Cloud Ops (The Brain)
* **April 22 (Day 1):** Provision the GCP project. **[UPGRADE]** Configure **Google Cloud Secret Manager** to distribute all API keys securely. Write the "Watcher" Python daemon to listen to the `/emergencies` collection.
* **April 23 (Day 2):** Scaffold the Vertex AI Agent Builder logic. Program it to query strictly for `status == "conflict"` and autonomously resolve resource overlaps.
* **April 24 (Day 3):** Finalize conflict logic and write the state-update script to flip documents back to `dispatched`.
* **April 25 (Day 4):** **[UPGRADE]** Implement the Fairness Check via Vertex AI Model Monitoring. **[UPGRADE]** Implement the **Human-in-the-Loop (HITL) Override**—if the AI flags a dispatch for high bias, change the status to `awaiting_human_approval`. **[DONE]** `audit.py` — `log_hitl_flag()` + `approve_dispatch()` + HITL daemon. Code Freeze.
* **April 26 (Day 5):** **The Splice (Integration).** Turn on your Watcher daemon. 
* **April 27 (Day 6):** Debug race conditions. Fix any database locking errors between your Orchestrator and Role 3's routing script. 

---

### Role 2: Triage Ingestion Lead (The Filter & Actuator)
* **April 22 (Day 1):** Write the feedparser script to pull live RSS alerts. Connect it to Gemini 1.5 Flash using `response_schema` to force perfect JSON outputs.
* **April 23 (Day 2):** Hook your script to Firestore. Push the JSON into `/emergencies` as `status: "triaged"`.
* **April 24 (Day 3):** **[UPGRADE] Build the Discord Actuator.** Write the daemon that listens to Firestore. When an emergency flips to `status: "dispatched"`, send an automated Discord embed to prove the AI has real-world agency.
* **April 25 (Day 4):** Code Freeze. Build a "Mock Data Spammer" script that injects 50 fake emergencies into Firestore to stress-test the system. Harden against rate limits. 
* **April 26 (Day 5):** **The Splice (Integration).** Turn on the firehose. Run your mock spammer so Roles 1, 3, and 4 have data to process.
* **April 27 (Day 6):** Fix any JSON parsing errors or database write limits found during stress testing.

---

### Role 3: Logistics & Prediction Lead (The Muscle & Forecaster)
* **April 22 (Day 1):** Create the `/resources` collection with mock emergency vehicles. Write the polling loop looking for `status == "triaged"`. 
* **April 23 (Day 2):** **[UPGRADE] Build the API Caching Layer** (check Firestore for similar recent routes before calling Google). Call the Google Maps Routes API to match vehicles and generate the polyline route.
* **April 24 (Day 3):** **[UPGRADE] Calculate SDG Impact.** Mathematically calculate the "Carbon/Fuel Emissions Saved" based on your routing efficiency. Set up Vertex AI AutoML Tabular for spread probability (or build a math mock endpoint if training takes too long).
* **April 25 (Day 4):** Pull live weather via OpenWeatherMap, feed it to Gemini 1.5 Pro for the "6-Hour Risk Assessment", and write all math back to Firestore. Code Freeze.
* **April 26 (Day 5):** **The Splice (Integration).** Boot your routing daemon.
* **April 27 (Day 6):** Ensure your scripts are perfectly writing the polyline routes, carbon math, and LLM text back to the right documents without crashing.

---

### Role 4: UI/UX & Communication Lead (The Glass)
* **April 22 (Day 1):** Initialize the dark-mode Streamlit app. **[UPGRADE] Mandate Mobile Responsiveness.** Ensure the layout collapses to a single column. Integrate pydeck/folium to dynamically map Role 3's routes.
* **April 23 (Day 2):** Set up Vertex AI Vector Search. Upload NDMA PDFs for the RAG context. Wire the RAG setup to autonomously draft Situation Reports (SitReps). 
* **April 24 (Day 3):** Build the "Upload Image" UI button wired to Gemini 1.5 Pro Vision. **[UPGRADE] Multi-Lingual Toggle:** Add the button to instantly translate the UI and SitReps into local languages (e.g., Hindi/Telugu) using Gemini.
* **April 25 (Day 4):** **[UPGRADE] Build the "Transparency-as-a-Service" panel** exposing the fairness audit. **[UPGRADE] Build the Live SDG Impact Counters** (Kg of CO2 prevented) and the Red HITL "Approve Dispatch" button. Code Freeze.
* **April 26 (Day 5):** **The Splice (Integration).** Boot the Streamlit UI. Ensure the polling loop does not crash when the DB is flooded by the other agents.
* **April 27 (Day 6):** Polish Day. Ensure map rendering is perfectly smooth, the terminal feed scrolls correctly, and Markdown looks professional.

---

### All Hands: April 28 (Submission Evening)
Dev work is strictly forbidden today.
1. [x] **The Golden Path:** Run a perfectly executed crisis simulation on the live app.
2. [x] **Record the Demo:** Do not edit fancy transitions. Show the mobile UI, show the Discord embed ping hitting the alert channel, click the "HITL Override" button, and highlight the SDG live trackers. Let the complex async code speak for itself.
3. [x] **Clean the Repo:** Clean up the GitHub README, ensure no `.env` files or API keys are public, and attach your architecture diagram.
4. [ ] **Submit:** Hit submit on the portal.