import React, { useState } from 'react';
import Header from '../components/Header';

const AssetTree = () => {
    const [selectedAsset, setSelectedAsset] = useState({
        id: 'SAT-8830-XL',
        name: 'AEGIS-02 THERMAL IMAGING',
        type: 'ORBITAL',
        status: 'ONLINE',
        connectivity: '99.8%',
        telemetry: {
            speed: '7.67 km/s',
            altitude: '542.1 km',
            battery: '84.2%',
            temp: '14.2°C'
        }
    });

    const [expanded, setExpanded] = useState({
        orbital: true,
        ground: true,
        field: true
    });

    const [command, setCommand] = useState('');
    const [commandStatus, setCommandStatus] = useState('IDLE');
    const [searchQuery, setSearchQuery] = useState('');
    const [isDiagnosing, setIsDiagnosing] = useState(false);
    const [isDeployingResource, setIsDeployingResource] = useState(false);

    const toggle = (section) => {
        setExpanded(prev => ({ ...prev, [section]: !prev[section] }));
    };

    const handleCommand = (e) => {
        if (e.key === 'Enter') {
            setCommandStatus('TRANSMITTING...');
            setTimeout(() => {
                setCommandStatus('ORCHESTRATING');
                setTimeout(() => setCommandStatus('IDLE'), 2000);
            }, 1000);
            setCommand('');
        }
    };

    const assets = {
        orbital: [
            { id: 'SAT-8829-XL', name: 'AEGIS-01 HIGH RESOLUTION', status: 'ONLINE', speed: '7.52 km/s', altitude: '540.2 km', battery: '92.1%', temp: '12.4°C' },
            { id: 'SAT-8830-XL', name: 'AEGIS-02 THERMAL IMAGING', status: 'ONLINE', speed: '7.67 km/s', altitude: '542.1 km', battery: '84.2%', temp: '14.2°C' },
            { id: 'SAT-8831-XL', name: 'AEGIS-03 LWS', status: 'MAINTENANCE', speed: '---', altitude: '538.9 km', battery: '45.0%', temp: '18.1°C' }
        ],
        ground: [
            { id: 'GSH-441-A', name: 'NORAD-HUB-01', status: 'ONLINE', type: 'GROUND' },
            { id: 'GSH-444-F', name: 'OSLO-HUB-04', status: 'OFFLINE', type: 'GROUND' }
        ]
    };

    const flattenFilter = (assetList) => {
        if (!searchQuery) return assetList;
        return assetList.filter(a => a.name.toLowerCase().includes(searchQuery.toLowerCase()) || a.id.toLowerCase().includes(searchQuery.toLowerCase()));
    };

    const triggerDiagnostics = async () => {
        setIsDiagnosing(true);
        try {
            const res = await fetch('http://localhost:8080/api/assets/diagnose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ asset_id: selectedAsset.id })
            });
            const data = await res.json();
            alert(`SYSLOG: Full diagnostic sweep complete for ${data.asset_id}.\n- Signal Integrity: ${data.diagnostics.signal_integrity}%\n- Logic Gate Sync: ${data.diagnostics.logic_gate_sync}\n- Internal Temp: ${data.diagnostics.internal_temp}°C\n- Drift: ${data.diagnostics.drift}%\n\nResult: ${data.diagnostics.result}`);
        } catch (e) {
            console.error(e);
            alert("DIAGNOSTICS FAILED: Could not reach control subsystem.");
        }
        setIsDiagnosing(false);
    };

    const handleExport = () => {
        const content = `SENTINEL_MIND REGISTRY DUMP\nDATE: ${new Date().toISOString()}\n\nORBITAL ASSETS:\n` + 
                        assets.orbital.map(a => `[${a.status}] ${a.id} - ${a.name}`).join('\n') + 
                        `\n\nGROUND STATIONS:\n` + 
                        assets.ground.map(a => `[${a.status}] ${a.id} - ${a.name}`).join('\n');
        const blob = new Blob([content], { type: 'text/plain' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `Registry_${Date.now()}.txt`;
        link.click();
    };

    const triggerDeploy = () => {
        setIsDeployingResource(true);
        setTimeout(() => setIsDeployingResource(false), 3000);
    };

    return (
        <div className="bg-[#EEF2F7] font-body-prose text-on-surface h-screen flex flex-col pt-14">
            <Header />

            <main className="flex flex-1 overflow-hidden">
                {/* Center Column: Asset Tree Explorer */}
                <div className="flex-1 flex flex-col bg-white border-r border-slate-200 relative z-40 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
                    <div className="h-16 px-6 border-b border-slate-100 bg-slate-50/30 backdrop-blur-md flex items-center gap-6">
                        <div className="flex flex-col min-w-max">
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">REGISTRY</span>
                            <span className="text-[14px] font-bold text-slate-900 leading-tight">ASSET EXPLORER</span>
                        </div>
                        
                        <div className="relative flex-1 group">
                            <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-black transition-colors text-[20px]">search</span>
                            <input 
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-11 pr-4 py-2 border border-slate-200 rounded-xl bg-white text-slate-800 focus:ring-1 focus:ring-black focus:border-black outline-none transition-all shadow-sm placeholder:text-slate-400 text-sm" 
                                placeholder="Search Satellite ID, Ground Station, or Fleet Tag..." 
                                type="text"
                            />
                        </div>
                        
                        <div className="flex items-center gap-2">
                            <button onClick={() => alert('Filtering: All Assets')} className="flex items-center gap-2 px-4 h-10 bg-white border border-slate-200 rounded-xl font-bold text-[11px] text-slate-600 hover:bg-slate-50 transition-all cursor-pointer shadow-sm hover:shadow active:scale-95 uppercase tracking-wider">
                                <span className="material-symbols-outlined text-[18px]">filter_list</span>
                                FILTERS
                            </button>
                            <button onClick={handleExport} className="p-2 h-10 w-10 flex items-center justify-center bg-white border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-all cursor-pointer shadow-sm hover:shadow active:scale-95">
                                <span className="material-symbols-outlined text-[20px]">ios_share</span>
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                        <div className="space-y-1">
                            <div onClick={() => toggle('orbital')} className="flex items-center gap-2 py-2 group cursor-pointer hover:bg-slate-100 px-2 rounded active:scale-[0.98] transition-transform">
                                <span className={`material-symbols-outlined text-slate-400 transition-transform duration-200 ${expanded.orbital ? 'rotate-0' : '-rotate-90'}`}>keyboard_arrow_down</span>
                                <span className="material-symbols-outlined text-blue-600">public</span>
                                <span className="font-bold text-[15px]">Orbital Fleet [O-NET]</span>
                                <span className="ml-auto font-mono text-[11px] text-slate-500">4/4 ACTIVE</span>
                            </div>
                            {expanded.orbital && flattenFilter(assets.orbital).map(asset => (
                                <div 
                                    key={asset.id}
                                    onClick={() => setSelectedAsset({
                                        id: asset.id,
                                        name: asset.name,
                                        status: asset.status,
                                        connectivity: asset.status === 'ONLINE' ? '99.8%' : '0.0%',
                                        telemetry: {
                                            speed: asset.speed,
                                            altitude: asset.altitude,
                                            battery: asset.battery,
                                            temp: asset.temp
                                        }
                                    })}
                                    className={`ml-8 flex items-center gap-3 py-2 px-4 hover:bg-slate-50 rounded border-l-2 cursor-pointer transition-all ${selectedAsset.id === asset.id ? 'bg-blue-50 border-blue-600' : 'border-transparent hover:border-blue-600'}`}
                                >
                                    <div className={`w-2 h-2 rounded-full ${asset.status === 'ONLINE' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-amber-500'}`}></div>
                                    <div className="flex flex-col">
                                        <span className="font-bold text-[12px] text-slate-800">{asset.name}</span>
                                        <span className="font-mono text-slate-500 text-[11px]">ID: {asset.id} | {asset.status}</span>
                                    </div>
                                    {asset.id === selectedAsset.id && (
                                        <span className="ml-auto material-symbols-outlined text-[18px] text-blue-600">radio_button_checked</span>
                                    )}
                                </div>
                            ))}

                            <div onClick={() => toggle('ground')} className="flex items-center gap-2 py-4 group cursor-pointer hover:bg-slate-100 px-2 rounded mt-4 active:scale-[0.98] transition-transform">
                                <span className={`material-symbols-outlined text-slate-400 transition-transform duration-200 ${expanded.ground ? 'rotate-0' : '-rotate-90'}`}>keyboard_arrow_down</span>
                                <span className="material-symbols-outlined text-blue-600">cell_tower</span>
                                <span className="font-bold text-[15px]">Ground Stations [G-BASE]</span>
                            </div>
                            {expanded.ground && flattenFilter(assets.ground).map(asset => (
                                <div 
                                    key={asset.id}
                                    onClick={() => setSelectedAsset({
                                        id: asset.id,
                                        name: asset.name,
                                        status: asset.status,
                                        connectivity: asset.status === 'ONLINE' ? '100%' : 'OFFLINE',
                                        telemetry: { speed: 'N/A', altitude: 'SEA LEVEL', battery: 'STATION POWER', temp: '22.0°C' }
                                    })}
                                    className={`ml-8 flex items-center gap-3 py-2 px-4 hover:bg-slate-50 rounded border-l-2 cursor-pointer transition-all ${selectedAsset.id === asset.id ? 'bg-blue-50 border-blue-600' : 'border-transparent'}`}
                                >
                                    <div className={`w-2 h-2 rounded-full ${asset.status === 'ONLINE' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`}></div>
                                    <div className="flex flex-col">
                                        <span className="font-bold text-[12px] text-slate-800">{asset.name}</span>
                                        <span className="font-mono text-slate-500 text-[11px]">ID: {asset.id} | {asset.status}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: Detail Panel */}
                <aside className="w-[400px] bg-white flex flex-col border-l border-slate-200 relative z-40 shadow-[-4px_0_24px_rgba(0,0,0,0.02)]">
                    <div className="p-6 border-b border-slate-100 bg-slate-50/50 backdrop-blur-sm">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 bg-primary rounded-full"></span>
                                <span className="text-[11px] font-black text-slate-400 tracking-[0.2em] uppercase">ASSET PROFILE</span>
                            </div>
                            <button onClick={() => alert('Panel reset to default.')} className="material-symbols-outlined text-slate-300 hover:text-slate-600 cursor-pointer transition-colors hover:bg-white p-1 rounded-md">close</button>
                        </div>
                        <h2 className="font-bold text-2xl text-slate-900 uppercase tracking-tight leading-none mb-1 line-clamp-1">{selectedAsset.name}</h2>
                        <p className="font-data-mono text-[11px] text-primary/60 font-bold tracking-widest uppercase">ID: {selectedAsset.id}</p>
                    </div>

                    <div className="flex-1 overflow-y-auto custom-scrollbar">
                        <section className="p-6 border-b border-slate-200">
                            <div className="flex items-center gap-2 mb-6">
                                <div className={`w-3 h-3 rounded-full animate-pulse ${selectedAsset.status === 'ONLINE' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
                                <span className={`font-bold text-[12px] uppercase tracking-wider ${selectedAsset.status === 'ONLINE' ? 'text-emerald-700' : 'text-amber-700'}`}>
                                    {selectedAsset.status}: {selectedAsset.connectivity}
                                </span>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 bg-slate-50 rounded border border-slate-200">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Metric A</p>
                                    <p className="font-mono text-lg text-slate-800">{selectedAsset.telemetry.speed}</p>
                                </div>
                                <div className="p-3 bg-slate-50 rounded border border-slate-200">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Metric B</p>
                                    <p className="font-mono text-lg text-slate-800">{selectedAsset.telemetry.altitude}</p>
                                </div>
                                <div className="p-3 bg-slate-50 rounded border border-slate-200">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Energy</p>
                                    <p className="font-mono text-lg text-slate-800">{selectedAsset.telemetry.battery}</p>
                                </div>
                                <div className="p-3 bg-slate-50 rounded border border-slate-200">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Stability</p>
                                    <p className="font-mono text-lg text-slate-800 font-bold text-emerald-600">NOMINAL</p>
                                </div>
                            </div>
                        </section>

                        <section className="p-6 border-b border-slate-200">
                            <h3 className="font-bold text-xs text-slate-400 uppercase mb-4 tracking-widest">Geospatial Reference</h3>
                            <div className="h-40 w-full bg-slate-100 rounded overflow-hidden relative border border-slate-200">
                                <div className="absolute inset-0 flex items-center justify-center bg-slate-50">
                                    <span className="material-symbols-outlined text-[48px] text-slate-200">map</span>
                                </div>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="w-4 h-4 bg-blue-600 rounded-full ring-4 ring-blue-600/20"></div>
                                </div>
                            </div>
                        </section>

                        <section className="p-6">
                            <h3 className="font-bold text-xs text-slate-400 uppercase mb-4 tracking-widest">Active Protocols</h3>
                            <div className="p-3 border border-blue-600/20 bg-blue-50/50 rounded flex items-start gap-3">
                                <span className="material-symbols-outlined text-blue-600 text-[20px]">verified_user</span>
                                <div>
                                    <p className="font-bold text-[12px] text-slate-800 tracking-tight">Mission Readiness Level 4</p>
                                    <p className="text-[11px] text-slate-500 mt-1">Resource is cleared for autonomous override and cross-sector dispatch.</p>
                                </div>
                            </div>
                        </section>
                    </div>

                    <div className="p-4 bg-white border-t border-slate-200 grid grid-cols-2 gap-2">
                        <button onClick={triggerDiagnostics} className="px-4 py-2 bg-white border border-slate-200 rounded font-bold text-[12px] text-slate-600 hover:bg-slate-50 transition-colors cursor-pointer active:scale-95 shadow-sm">
                            {isDiagnosing ? 'SCANNING...' : 'DIAGNOSTICS'}
                        </button>
                        <button onClick={() => {
                            alert(`ATTENTION: Override signal sent to ${selectedAsset.id}. Manual control established over telemetry node ${selectedAsset.id.split('-')[1]}.`);
                        }} className="px-4 py-2 bg-blue-600 text-white rounded font-bold text-[12px] hover:bg-blue-700 transition-all cursor-pointer shadow-md active:scale-95 border border-transparent">
                            OVERRIDE
                        </button>
                    </div>
                </aside>
            </main>
            
            {/* Standardized Command Bar */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-5xl h-20 frosted border border-white/60 rounded-2xl shadow-2xl z-[100] flex items-center px-6 gap-6">
                <button onClick={triggerDeploy} className="h-12 bg-primary text-white text-[12px] font-bold px-6 rounded-xl flex items-center gap-3 hover:bg-primary/90 transition-all active:scale-95 shadow-lg shadow-primary/20 whitespace-nowrap">
                    <span className={`material-symbols-outlined ${isDeployingResource ? 'animate-spin' : ''}`}>sync</span>
                    {isDeployingResource ? 'DEPLOYING...' : 'RESOURCE DEPLOY'}
                </button>
                <div className="flex-1 h-12 bg-white/40 border border-brand-border rounded-xl px-4 flex items-center overflow-hidden focus-within:ring-1 focus-within:ring-primary">
                    <span className={`font-data-mono mr-2 ${commandStatus !== 'IDLE' ? 'text-emerald-500 animate-pulse' : 'text-primary'}`}>{commandStatus === 'IDLE' ? '_' : '>'}</span>
                    <input 
                        value={commandStatus !== 'IDLE' ? commandStatus : command}
                        disabled={commandStatus !== 'IDLE'}
                        onChange={(e) => setCommand(e.target.value)}
                        onKeyDown={handleCommand}
                        className="bg-transparent border-none outline-none w-full font-data-mono text-sm text-slate-800 placeholder-slate-400 uppercase tracking-wider" 
                        placeholder="Issue asset orchestrator command..." 
                        type="text"
                    />
                </div>
                <div className="flex gap-4 border-l border-brand-border pl-6">
                    <div className="text-right">
                        <span className="block text-[18px] font-data-mono leading-none">0/4</span>
                        <span className="block text-[8px] font-bold text-slate-500 tracking-wider">DEPLOYED</span>
                    </div>
                    <div className="text-right">
                        <span className="block text-[18px] font-data-mono leading-none">100%</span>
                        <span className="block text-[8px] font-bold text-slate-500 tracking-wider uppercase">HEALTH</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssetTree;
