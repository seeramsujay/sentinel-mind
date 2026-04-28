import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

const FieldUpload = () => {
    const [progress, setProgress] = useState(0);
    const [isDeploying, setIsDeploying] = useState(false);
    const [statusText, setStatusText] = useState("Awaiting cloud deployment orchestration...");
    const [previewUrl, setPreviewUrl] = useState("https://lh3.googleusercontent.com/aida-public/AB6AXuDFcfCaVGsX6cvaTIqxJJ0IrgxPniIR6C1hJuA9iqhmhCjQ99am3v01QsVGYQJo3bj8PJz0DmmY2Q9MaSizku06Z3NYg6vthdZzOMEAa1K1YSDIJFWNd2hSXITGn3c1Tj6A8hjXIaQyPNvg6mHzu5PpRVDjC_tAes0E0j1kNLRI904SRu-T84Wj2XKhBM7GvI5ZDX7U1O3cZsxnVqHgpnAaxTdTUlZtPVI7pZ6frnxoGVMb4wwTaN2FWShR-nAptMpDagKD7mzFcv8");
    const [metadata, setMetadata] = useState(null);

    const onFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreviewUrl(reader.result);
                setProgress(0);
                setStatusText(`IMAGE_SOURCE: ${file.name} CACHED`);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleDeploy = async () => {
        if (isDeploying) return;
        setIsDeploying(true);
        setStatusText("INITIATING CLOUD HANDSHAKE...");
        setProgress(10);

        try {
            let b64 = "";
            let mime = "image/jpeg";
            
            if (previewUrl.startsWith('data:')) {
                b64 = previewUrl.split(',')[1];
                mime = previewUrl.split(';')[0].split(':')[1];
            } else if (previewUrl.startsWith('http')) {
                // Handle the default placeholder image gracefully
                setStatusText("PROCESSING SYSTEM ASSET...");
                b64 = "MOCK_BASE64_FOR_DEMO"; 
            } else {
                throw new Error("Invalid source data. Please reload the image.");
            }

            setProgress(30);
            const res = await fetch('https://sentinel-mind-51884867643.us-central1.run.app/api/vision/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_b64: b64, mime_type: mime })
            });

            setProgress(70);
            if (!res.ok) throw new Error("Backend offline");

            const data = await res.json();

            setMetadata(data);
            setProgress(100);
            setStatusText("DEPLOYMENT COMPLETE: METADATA EXTRACTED");
        } catch (e) {
            console.error(e);
            setStatusText("UPLOAD FAILED - CHECK BACKEND");
            setProgress(0);
        }
        setIsDeploying(false);
    };

    const random = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);

    const handleExport = () => {
        const logContent = `SENTINEL_MIND SYSTEM LOG - ${new Date().toISOString()}\n\nSource: Field Operator Unit-7\nSymmetry Key: AEGIS-SEC-01\n\n[INFO] Data Packet IMG_ZONE_NORTH_01.RAW cached.\n[INFO] AI Confidence: 94.2%\n[WARN] High thermal variance in sector 4.\n[INFO] Deployment readiness: 100%\n\n--- END LOG ---`;
        const blob = new Blob([logContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `terminal_log_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        alert("TERMINAL_LOG_EXPORT: Data saved to local storage.");
    };

    return (
        <div className="bg-[#EEF2F7] font-body-medium text-slate-800 h-screen overflow-hidden flex flex-col pt-14">
            <Header />
            <input
                type="file"
                id="field-image-input"
                className="hidden"
                accept="image/*"
                onChange={onFileSelect}
            />

            {/* Main Content Area */}
            <main className="flex-1 flex overflow-hidden">
                {/* Center Column: Vision Entry (75%) */}
                <section className="flex-1 flex flex-col bg-white border-r border-slate-200 overflow-hidden relative z-40">
                    {/* Internal Top Panel */}
                    <div className="h-16 px-6 border-b border-slate-100 bg-slate-50/30 backdrop-blur-md flex items-center justify-between">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">OPERATOR PANEL</span>
                            <h1 className="text-[18px] font-bold text-slate-900 leading-tight">VISION GATEWAY_ALPHA</h1>
                        </div>
                        <div className="flex gap-3">
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-[10px] font-bold border border-blue-100">
                                <span className={`w-1.5 h-1.5 rounded-full bg-blue-500 ${isDeploying ? 'animate-ping' : 'animate-pulse'}`}></span>
                                {isDeploying ? 'SYNCING...' : 'UPLINK_STABLE'}
                            </div>
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-[10px] font-bold border border-emerald-100">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                ENCRYPTED
                            </div>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-8 custom-scrollbar space-y-8">
                        {/* Large Upload Area */}
                        <div onClick={() => document.getElementById('field-image-input').click()} className="h-[400px] bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center group cursor-pointer transition-all hover:border-black hover:bg-white shadow-sm">
                            {/* Scanning Line Animation */}
                            <div className="absolute top-0 left-0 w-full h-0.5 bg-black/10 animate-[scan_3s_ease-in-out_infinite]"></div>

                            {/* Hexagonal Target & Image Preview */}
                            <div className="relative w-full h-full flex items-center justify-center">
                                {previewUrl && (
                                    <img 
                                        src={previewUrl} 
                                        alt="Field Intel" 
                                        className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                                    />
                                )}
                                
                                <div className="relative w-48 h-48 flex items-center justify-center z-20">
                                    <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                                        <polygon className="group-hover:stroke-blue-600 transition-colors" fill="none" points="50,5 93,30 93,70 50,95 7,70 7,30" stroke="#2563eb" strokeDasharray="4 4" strokeWidth="1.5"></polygon>
                                    </svg>
                                    <div className={`flex flex-col items-center gap-3 ${previewUrl ? 'text-white' : 'text-blue-600'}`}>
                                        <span className="material-symbols-outlined text-5xl">cloud_upload</span>
                                        <span className="font-bold text-[10px] tracking-widest uppercase font-ui-label-bold">
                                            {previewUrl ? 'UPLOADED_READY' : 'Drop Imagery'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-8 text-center relative z-20">
                                <p className="font-bold text-slate-800 font-data-mono text-sm tracking-tighter">DRAG_AND_DROP_FIELD_DATA</p>
                                <p className="text-slate-400 text-[10px] mt-1 font-data-mono opacity-60">SUPPORTED: RAW, JPG, NITF-2.1, PNG | MAX_SIZE: 50MB</p>
                            </div>

                            {/* Processing State Footer */}
                            <div className="absolute bottom-12 w-full px-24">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-data-terminal text-[9px] text-blue-600 font-bold uppercase tracking-widest">
                                        {isDeploying ? "Uploading Telemetry..." : (progress === 100 ? "Deployment Complete" : "Awaiting Data Upload")}
                                    </span>
                                    <span className="font-data-terminal text-[9px] text-blue-600 font-bold">{progress}%</span>
                                </div>
                                <div className="h-1 bg-blue-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-600 transition-all duration-300" style={{ width: `${progress}%` }}></div>
                                </div>
                            </div>
                        </div>

                        {/* Quick Access Assets */}
                        <div className="grid grid-cols-4 gap-4 pb-20">
                            {[1, 2].map(i => (
                                <div key={i} onClick={() => alert(`Reviewing source IMG_ZONE_NORTH_0${i}.RAW`)} className="bg-white border border-[#DDE3EE] rounded p-3 flex flex-col justify-between hover:border-blue-400 transition-all cursor-pointer shadow-sm active:scale-95 transition-transform">
                                    <div className="flex justify-between items-start">
                                        <span className="material-symbols-outlined text-slate-300 text-lg">image</span>
                                        <span className="text-[9px] font-data-mono text-slate-400">{i * 6}.4 MB</span>
                                    </div>
                                    <p className="text-[9px] font-data-terminal text-slate-600 truncate uppercase mt-2">IMG_ZONE_NORTH_0{i}.RAW</p>
                                </div>
                            ))}
                            <div onClick={() => alert('Protocol Alpha: Add New Feed Source')} className="bg-white border border-[#DDE3EE] border-dashed rounded p-3 flex items-center justify-center text-slate-400 hover:text-blue-600 hover:border-blue-300 transition-all cursor-pointer active:scale-95 transition-transform">
                                <span className="material-symbols-outlined">add_circle</span>
                            </div>
                            <div onClick={() => alert('Accessing Telemetry History Logs')} className="bg-slate-50 border border-[#DDE3EE] rounded p-3 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-all cursor-pointer active:scale-95 transition-transform">
                                <span className="material-symbols-outlined">history</span>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Right Column: Metadata Detail Pane (320px) */}
                <section className="w-[320px] bg-white p-6 flex flex-col gap-6 relative z-40 border-l border-slate-200">
                    <div className="flex-1 overflow-y-auto custom-scrollbar">
                        <h3 className="font-ui-label-bold text-[10px] uppercase tracking-widest text-slate-400 mb-6 font-bold">Extracted Metadata</h3>
                        {metadata ? (
                            <div className="space-y-4 font-data-terminal text-[11px]">
                                <div className="p-3 bg-slate-50 border border-slate-100 rounded">
                                    <p className="text-slate-400 mb-1 text-[9px] uppercase tracking-tighter font-bold">COORDINATE_FIX</p>
                                    <div className="flex justify-between items-center text-slate-900 font-bold">
                                        <span>{metadata.extracted_coordinates || 'N/A'}</span>
                                        <span className="material-symbols-outlined text-emerald-500 text-sm">location_on</span>
                                    </div>
                                </div>

                                <div className="p-3 bg-slate-50 border border-slate-100 rounded">
                                    <p className="text-slate-400 mb-1 text-[9px] uppercase tracking-tighter font-bold">AI Confidence Score</p>
                                    <div className="flex items-center gap-3">
                                        <div className="flex-grow h-1 bg-slate-200 rounded-full overflow-hidden">
                                            <div className="h-full bg-emerald-500 transition-all" style={{ width: `${metadata.confidence || 0}%` }}></div>
                                        </div>
                                        <span className="text-emerald-600 font-bold">{metadata.confidence || 0}%</span>
                                    </div>
                                </div>

                                <div className="p-3 bg-slate-50 border border-slate-100 rounded">
                                    <p className="text-slate-400 mb-1 text-[9px] uppercase tracking-tighter font-bold">Detected Objects / Analysis</p>
                                    <div className="space-y-2 mt-2">
                                        {(metadata.objects_detected || ["No hazards identified"]).map((obj, i) => (
                                            <div key={i} className="flex justify-between text-blue-600 font-bold">
                                                <span>{obj}</span>
                                                <span className="opacity-70 text-[9px]">[SCANNED]</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4 font-data-terminal text-[11px]">
                                <div className="p-3 bg-slate-50 border border-slate-100 rounded">
                                    <p className="text-slate-400 mb-1 text-[9px] uppercase tracking-tighter font-bold">COORDINATE_FIX</p>
                                    <div className="flex justify-between items-center text-slate-400 font-bold">
                                        <span>AWAITING TELEMETRY</span>
                                    </div>
                                </div>
                                <div className="p-3 bg-slate-50 border border-slate-100 rounded">
                                    <p className="text-slate-400 mb-1 text-[9px] uppercase tracking-tighter font-bold">AI Confidence Score</p>
                                    <div className="flex items-center gap-3">
                                        <div className="flex-grow h-1 bg-slate-200 rounded-full overflow-hidden"></div>
                                        <span className="text-emerald-600 font-bold">0%</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="aspect-video w-full bg-slate-50 text-slate-400 flex items-center justify-center font-bold text-[10px] tracking-widest rounded-lg border border-slate-200 mt-6 overflow-hidden">
                            METADATA_ANALYSIS_PENDING
                        </div>
                    </div>

                    <div className="pt-4 mt-auto">
                        <button onClick={handleExport} className="w-full bg-white border border-slate-200 text-slate-800 py-4 rounded-xl font-data-terminal text-[10px] tracking-[2px] uppercase shadow-sm hover:bg-slate-50 transition-all cursor-pointer active:scale-95">
                            Export_Terminal_Log
                        </button>
                    </div>
                </section>
            </main>

            {/* Standardized Command Bar */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-5xl h-20 frosted border border-white/60 rounded-2xl shadow-2xl z-[100] flex items-center px-6 gap-6">
                <button
                    onClick={handleDeploy}
                    disabled={isDeploying}
                    className={`h-12 ${isDeploying ? 'bg-slate-400 cursor-not-allowed' : 'bg-primary hover:bg-primary/90'} text-white text-[12px] font-bold px-8 rounded-xl flex items-center gap-3 transition-all active:scale-95 shadow-lg shadow-primary/20 whitespace-nowrap`}
                >
                    <span className="material-symbols-outlined">{isDeploying ? 'sync' : 'rocket_launch'}</span>
                    {isDeploying ? 'DEPLOYING...' : 'DEPLOY_DATA'}
                </button>
                <div className="flex-1 h-12 bg-white/40 border border-brand-border rounded-xl px-4 flex items-center">
                    <span className={`font-data-terminal text-[10px] ${isDeploying ? 'text-primary animate-pulse' : 'text-slate-400'} uppercase tracking-widest`}>
                        {statusText}
                    </span>
                </div>
                <div className="flex gap-4 border-l border-brand-border pl-6">
                    <div className="text-right">
                        <span className="block text-[18px] font-data-mono leading-none">{progress}%</span>
                        <span className="block text-[8px] font-bold text-slate-500 tracking-wider">SYNC</span>
                    </div>
                    <div className="text-right">
                        <span className="block text-[18px] font-data-mono leading-none text-emerald-600">SECURE</span>
                        <span className="block text-[8px] font-bold text-slate-500 tracking-wider uppercase">CHANNEL</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FieldUpload;
