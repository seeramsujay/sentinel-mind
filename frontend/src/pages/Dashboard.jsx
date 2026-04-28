import React, { useState, useEffect } from 'react';
import { GoogleMap, useJsApiLoader, OverlayViewF } from '@react-google-maps/api';
import { collection, onSnapshot, query, limit } from 'firebase/firestore';
import { db } from '../firebase';
import { useLocation } from 'react-router-dom';
import Header from '../components/Header';

function App() {
  const [emergencies, setEmergencies] = useState([]);
  const [selectedInc, setSelectedInc] = useState(null);
  const [command, setCommand] = useState('');
  
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const urgencyFilter = searchParams.get('urgency');

  const filteredEmergencies = urgencyFilter 
    ? emergencies.filter(e => e.urgency === urgencyFilter)
    : emergencies;

  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
  });

  useEffect(() => {
    const q = query(collection(db, 'emergencies'));
    const unsubscribe = onSnapshot(q, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setEmergencies(data);
      if (data.length > 0) {
        setSelectedInc(prev => prev || data[0]);
      }
    }, (error) => {
      console.error("Firebase Snapshot Error:", error);
    });
    
    return () => unsubscribe();
  }, []);

  const [showLog, setShowLog] = useState(false);

  useEffect(() => {
    // Reset log view when selected incident changes
    setShowLog(false);
  }, [selectedInc]);

  const handleCommand = (e) => {
    if (e.key === 'Enter') {
      alert(`Orchestration Command Issued: ${command}\n\nStatus: Awaiting System Triage...`);
      setCommand('');
    }
  };

  const navigateToUpload = () => {
    window.location.href = "/upload";
  };

  return (
    <div className="bg-brand-canvas text-on-surface font-body-prose overflow-hidden h-screen flex flex-col pt-14">
      <Header />

      <main className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Agent Feed remains same */}
        <aside className="w-[280px] bg-slate-50 border-r border-brand-border flex flex-col overflow-hidden relative z-40">
          <div className="p-4 border-b border-brand-border bg-white">
            <h2 className="font-ui-label-bold text-[12px] text-slate-500 uppercase tracking-widest font-bold">AGENT FEED</h2>
            <div className="mt-2 flex items-center justify-between text-[10px] font-data-terminal text-slate-400 uppercase">
              <span>Active Stream</span>
              <span className="text-blue-600">Syncing...</span>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 font-data-terminal text-[12px] terminal-scroll space-y-3 custom-scrollbar">
            {filteredEmergencies.map((e, idx) => (
              <div 
                key={e.id || idx} 
                onClick={() => setSelectedInc(e)}
                className={`border-l-2 pl-3 py-2 space-y-1 bg-white shadow-sm cursor-pointer transition-all hover:translate-x-1 ${
                  e.id === selectedInc?.id ? 'border-primary ring-1 ring-primary/10' : 
                  e.urgency === 'P1' ? 'border-error' : 
                  e.urgency === 'P2' ? 'border-orange-500' : 'border-slate-300'
                }`}
              >
                <div className="flex justify-between opacity-60 text-[10px]">
                  <span>[{e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : 'LIVE'}]</span>
                  <span className={e.urgency === 'P1' ? 'text-error font-bold' : 'text-blue-600'}>{e.status?.toUpperCase() || 'TRIAGE'}</span>
                </div>
                <p className="text-slate-800 font-medium truncate">{e.hazard_type}: {e.location_coordinates?.lat?.toFixed(2) || 'Sector 7G'}</p>
                <p className="text-[10px] text-slate-500 truncate">{e.description || 'Analyzing sensor anomaly...'}</p>
              </div>
            ))}
          </div>
        </aside>

        {/* Center Panel: Tactical Grid remains same */}
        <section className="flex-1 relative bg-[#E8EFF9] overflow-hidden">
          {isLoaded && (
            <GoogleMap
              mapContainerStyle={{ width: '100%', height: '100%' }}
              center={{ lat: 20.5937, lng: 78.9629 }}
              zoom={5}
              options={{ disableDefaultUI: true }}
            >
              {filteredEmergencies.map((e, idx) => {
                const lon = Number(e.location_coordinates?.lng || e.location?.lng || e.location?.longitude);
                const lat = Number(e.location_coordinates?.lat || e.location?.lat || e.location?.latitude);
                if (isNaN(lon) || isNaN(lat)) return null;

                return (
                  <OverlayViewF
                    position={{ lat, lng: lon }}
                    mapPaneName={OverlayViewF.OVERLAY_MOUSE_TARGET}
                    key={e.id || idx}
                  >
                    <div 
                      style={{ transform: 'translate(-50%, -50%)' }}
                      className="group cursor-pointer"
                      onClick={() => setSelectedInc(e)}
                    >
                      <div className="relative flex items-center justify-center">
                         <div className={`absolute w-14 h-14 rounded-full pulsing ${e.urgency === 'P1' ? 'bg-red-500/20' : 'bg-blue-500/10'}`}></div>
                         <div className={`w-3.5 h-3.5 rounded-full border-2 border-white shadow-lg transition-transform group-hover:scale-125 ${e.urgency === 'P1' ? 'bg-error' : 'bg-blue-600'}`}></div>
                         <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-white px-2 py-1 rounded shadow-sm border border-brand-border whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-50">
                           <span className="font-bold text-[10px] uppercase text-slate-900">{e.hazard_type}</span>
                         </div>
                      </div>
                    </div>
                  </OverlayViewF>
                );
              })}
            </GoogleMap>
          )}

          {/* Frosted Glass Overlay: Swarm Status */}
          <div className="absolute top-6 left-6 frosted p-4 border border-white/50 rounded-xl shadow-lg w-64 z-40">
            <div className="flex items-center justify-between mb-4">
              <span className="font-bold text-[12px] uppercase tracking-tight">LIVE SWARM STATUS</span>
              <span className="material-symbols-outlined text-blue-600">hub</span>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between font-data-terminal text-[10px] mb-1">
                  <span>COHESION</span>
                  <span>98%</span>
                </div>
                <div className="h-1 bg-blue-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 w-[98%]"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between font-data-terminal text-[10px] mb-1">
                  <span>LATENCY (AVG)</span>
                  <span>14ms</span>
                </div>
                <div className="h-1 bg-blue-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 w-[14%]"></div>
                </div>
              </div>
              <div className="flex gap-2 pt-2">
                <div className="flex-1 bg-white/40 border border-white p-2 rounded">
                  <span className="block text-[18px] font-data-mono">24</span>
                  <span className="block text-[8px] font-bold text-slate-500 uppercase tracking-tight">AGENTS</span>
                </div>
                <div className="flex-1 bg-white/40 border border-white p-2 rounded">
                  <span className="block text-[18px] font-data-mono">08</span>
                  <span className="block text-[8px] font-bold text-slate-500 uppercase tracking-tight">ZONES</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Right Sidebar: SitReps */}
        <aside className="w-[320px] bg-white border-l border-brand-border flex flex-col relative z-40">
          <div className="p-4 border-b border-brand-border bg-slate-50/50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-[12px] uppercase">Transparency</h2>
              <span className="material-symbols-outlined text-sm text-slate-400">info</span>
            </div>
            <div className="space-y-4">
              {['Northern Perimeter', 'Urban Core Logistics'].map(zone => (
                <div key={zone}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-body-medium text-[12px]">{zone}</span>
                    <span className="bg-blue-50 text-blue-600 text-[9px] px-1.5 py-0.5 rounded font-bold">OPTIMIZED</span>
                  </div>
                  <div className="relative h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div className="absolute inset-0 bg-blue-100 w-[85%]"></div>
                    <div className="absolute inset-0 bg-blue-600 w-[62%] transition-all"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-brand-border bg-white flex items-center justify-between">
              <h2 className="font-bold text-[12px] uppercase">RAG SitReps</h2>
              <span className="text-[10px] font-data-mono text-slate-400">Total: {filteredEmergencies.length}</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
              {selectedInc ? (
                <div className="p-3 border border-primary border-2 rounded-xl bg-white shadow-md transition-all">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold border ${selectedInc.urgency === 'P1' ? 'bg-red-50 text-error border-red-100' : 'bg-blue-50 text-blue-600 border-blue-100'}`}>
                      {selectedInc.urgency === 'P1' ? 'CRITICAL' : 'ROUTINE'}
                    </span>
                    <span className="font-data-mono text-[10px] text-slate-400">LIVE</span>
                  </div>
                  <h3 className="font-bold text-[15px] text-slate-900 mb-1 leading-tight">{selectedInc.hazard_type || 'Unknown Event'}</h3>
                  <p className="text-[12px] text-slate-500 mb-3 leading-relaxed">
                    {selectedInc.intelligence?.situation_report || selectedInc.description || 'Assessing context...'}
                  </p>
                  
                  {showLog && (
                    <div className="mb-3 px-3 py-2 bg-blue-50/30 rounded border border-blue-100 animate-in fade-in slide-in-from-top-2 duration-300">
                       <p className="text-[9px] font-bold text-blue-600 uppercase mb-1 flex items-center gap-1">
                         <span className="material-symbols-outlined text-[10px]">terminal</span>
                         System Audit Log
                       </p>
                       <p className="text-[10px] text-slate-600 italic tracking-tight leading-normal">
                         {selectedInc.intelligence?.ndma_protocol || `Mission protocol initialized. Syncing with regional node SE-INDIA-0${Math.floor(Math.random()*9)}...`}
                       </p>
                       <p className="text-[9px] text-slate-400 mt-2 font-data-mono uppercase">Node: SE-INDIA-07 | Port: 443</p>
                    </div>
                  )}
                  
                  <div className="pt-3 border-t border-brand-border flex items-center justify-between">
                    <div className="flex-1 pr-4">
                      <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                        <span>CONFIDENCE</span>
                        <span>{selectedInc.intelligence?.risk_score || '92'}%</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 transition-all duration-1000" style={{ width: `${selectedInc.intelligence?.risk_score || 92}%` }}></div>
                      </div>
                    </div>
                    <button 
                      onClick={() => setShowLog(!showLog)} 
                      className={`material-symbols-outlined hover:text-primary transition-all cursor-pointer active:scale-90 p-1 rounded-full ${showLog ? 'text-primary bg-primary/5 rotate-90' : 'text-slate-400'}`}
                      title={showLog ? "Hide Logic Logs" : "Expand Logic Logs"}
                    >
                      arrow_forward
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-10 text-center opacity-20 flex flex-col items-center">
                   <span className="material-symbols-outlined text-[48px] mb-2">analytics</span>
                   <span className="text-[12px] font-bold uppercase tracking-widest">Select Incident</span>
                </div>
              )}
              {filteredEmergencies.filter(e => e.id !== selectedInc?.id).slice(0, 10).map((e, idx) => (
                <div key={idx} onClick={() => setSelectedInc(e)} className="p-3 border border-brand-border rounded-xl bg-white shadow-sm hover:border-primary/30 transition-all cursor-pointer group">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`text-[9px] px-2 py-0.5 rounded font-bold border ${e.urgency === 'P1' ? 'bg-red-50 text-error border-red-50' : 'bg-slate-50 text-slate-400 border-slate-100'} uppercase`}>
                      {e.urgency === 'P1' ? 'CRITICAL' : e.hazard_type}
                    </span>
                    <span className="font-data-mono text-[10px] text-slate-400">STATE: {e.status?.toUpperCase()}</span>
                  </div>
                  <h3 className="font-bold text-[13px] text-slate-800 group-hover:text-primary transition-colors">
                    {e.location_coordinates?.lat?.toFixed(2)}N, {e.location_coordinates?.lng?.toFixed(2)}E
                  </h3>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">{e.description || 'Telemetry archived.'}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </main>

      {/* Command Bar */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-5xl h-20 frosted border border-white/60 rounded-2xl shadow-2xl z-[100] flex items-center px-6 gap-6">
        <button onClick={navigateToUpload} className="h-12 bg-primary text-white text-[12px] font-bold px-6 rounded-xl flex items-center gap-3 hover:bg-primary/90 transition-all active:scale-95 shadow-lg shadow-primary/20 whitespace-nowrap">
          <span className="material-symbols-outlined">cloud_upload</span>
          UPLOAD FIELD IMAGE
        </button>
        <div className="flex-1 h-12 bg-white/40 border border-brand-border rounded-xl px-4 flex items-center overflow-hidden focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
          <span className="font-data-mono text-primary mr-2">_</span>
          <input 
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={handleCommand}
            className="bg-transparent border-none outline-none w-full font-data-mono text-sm text-slate-800 placeholder-slate-400 uppercase tracking-wider" 
            placeholder="Issue orchestrator command..." 
            type="text"
          />
        </div>
        <div className="flex gap-4 border-l border-brand-border pl-6">
          <div className="text-right">
            <span className="block text-[18px] font-data-mono leading-none">2.4m</span>
            <span className="block text-[8px] font-bold text-slate-500 tracking-wider">AVG RESPONSE</span>
          </div>
          <div className="text-right">
            <span className="block text-[18px] font-data-mono leading-none">{emergencies.filter(e => e.status === 'dispatched').length || '148'}</span>
            <span className="block text-[8px] font-bold text-slate-500 tracking-wider uppercase">Active Agents</span>
          </div>
          <div className="text-right">
            <span className="block text-[18px] font-data-mono leading-none text-emerald-600">92%</span>
            <span className="block text-[8px] font-bold text-slate-500 tracking-wider uppercase">Resolved</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
