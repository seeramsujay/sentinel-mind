import React from 'react';
import { Link } from 'react-router-dom';

const Register = () => {
    return (
        <div className="bg-surface-container-lowest min-h-screen flex overflow-hidden">
        {/* Left Half: Tactical Map Section (60vw) */}
        <section className="w-[60vw] relative bg-gradient-to-br from-[#0D1B2E] to-[#1A2E50] hidden lg:flex flex-col justify-between p-12 overflow-hidden border-r border-slate-800">
        {/* Hex Grid Overlay */}
        <div className="absolute inset-0 opacity-30">
            <svg width="100%" height="100%">
                <pattern id="hex" width="60" height="104" patternUnits="userSpaceOnUse">
                    <path d="M30 0l30 17.32v34.64L30 69.28 0 51.96V17.32L30 0z" fillOpacity="0.05" fill="#ffffff" fillRule="evenodd" />
                </pattern>
                <rect width="100%" height="100%" fill="url(#hex)" />
            </svg>
        </div>
        {/* Massive Watermark Hexagon */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] opacity-[0.08]">
        <svg className="w-full h-full fill-white" viewBox="0 0 100 115">
        <polygon points="50 0 100 28.87 100 86.6 50 115.47 0 86.6 0 28.87"></polygon>
        </svg>
        </div>
        {/* Tactical Map Elements (SVG Lines & Pulse Markers) */}
        <div className="absolute inset-0">
        <svg className="w-full h-full opacity-40">
        <path d="M 200,200 L 450,350 L 700,150 L 900,450" fill="none" stroke="white" strokeDasharray="8,8" strokeWidth="1.5"></path>
        <path d="M 100,600 L 300,550 L 500,750" fill="none" stroke="white" strokeDasharray="8,8" strokeWidth="1.5"></path>
        </svg>
        <div className="absolute w-3 h-3 bg-blue-600 rounded-full" style={{top: "200px", left: "200px"}}><div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 border-2 border-blue-600 rounded-full animate-ping opacity-80"></div></div>
        <div className="absolute w-3 h-3 bg-blue-600 rounded-full" style={{top: "350px", left: "450px"}}><div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 border-2 border-blue-600 rounded-full animate-ping opacity-80" style={{animationDelay: "0.5s"}}></div></div>
        <div className="absolute w-3 h-3 bg-blue-600 rounded-full" style={{top: "150px", left: "700px"}}><div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 border-2 border-blue-600 rounded-full animate-ping opacity-80" style={{animationDelay: "1.5s"}}></div></div>
        <div className="absolute w-3 h-3 bg-blue-600 rounded-full" style={{top: "550px", left: "300px"}}><div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 border-2 border-blue-600 rounded-full animate-ping opacity-80" style={{animationDelay: "2s"}}></div></div>
        </div>
        {/* Brand Footer */}
        <div className="relative z-10 mt-auto flex items-center gap-4">
        <div className="w-14 h-14 flex items-center justify-center bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
        <span className="material-symbols-outlined text-white text-4xl" data-weight="fill" style={{fontVariationSettings: "'FILL' 1"}}>hexagon</span>
        </div>
        <div>
        <h1 className="font-display-brand text-white text-3xl tracking-tighter uppercase font-extrabold">SENTINELMIND</h1>
        <p className="text-[12px] font-bold text-blue-300 uppercase tracking-[0.2em] opacity-80">Orchestrating calm from chaos</p>
        </div>
        </div>
        </section>

        {/* Right Half: Form Section (40vw) */}
        <main className="w-full lg:w-[40vw] bg-[#EEF2F7] flex items-center justify-center p-6 md:p-12 overflow-y-auto">
        <div className="w-full max-w-[480px]">
        {/* Responsive Mobile Logo */}
        <div className="lg:hidden flex flex-col items-center mb-8">
        <span className="material-symbols-outlined text-blue-600 text-5xl mb-2" data-weight="fill" style={{fontVariationSettings: "'FILL' 1"}}>hexagon</span>
        <h1 className="font-display-brand text-[#191b23] text-2xl font-extrabold">SENTINELMIND</h1>
        </div>

        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8 transition-all duration-300">
        {/* Desktop Header */}
        <div className="hidden lg:flex items-center gap-3 mb-10">
        <span className="material-symbols-outlined text-blue-600 text-3xl" data-weight="fill" style={{fontVariationSettings: "'FILL' 1"}}>hexagon</span>
        <h2 className="font-display-brand text-[#191b23] text-xl font-extrabold uppercase">SENTINELMIND</h2>
        </div>

        {/* Tab Switcher */}
        <div className="flex p-1 bg-[#f3f3fe] rounded-lg mb-8">
        <Link to="/" className="flex-1 py-2 text-center text-[12px] font-bold text-slate-500 rounded-lg hover:bg-white/50 transition-all">Sign In</Link>
        <button className="flex-1 py-2 text-center text-[12px] font-bold bg-blue-600 text-white rounded-lg shadow-sm">Create Account</button>
        </div>

        <form className="space-y-5">
        {/* Full Name */}
        <div>
        <label className="block text-[12px] font-bold text-slate-600 mb-1.5 ml-1">Full Name</label>
        <input className="w-full h-11 bg-[#F6F8FC] border border-slate-200 rounded-lg px-4 font-mono text-slate-800 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all placeholder:text-slate-400" placeholder="Commander Name" type="text"/>
        </div>
        {/* Email */}
        <div>
        <label className="block text-[12px] font-bold text-slate-600 mb-1.5 ml-1">Work Email</label>
        <input className="w-full h-11 bg-[#F6F8FC] border border-slate-200 rounded-lg px-4 font-mono text-slate-800 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all placeholder:text-slate-400" placeholder="name@organization.gov" type="email"/>
        </div>

        {/* Role Dropdown */}
        <div>
        <label className="block text-[12px] font-bold text-slate-600 mb-1.5 ml-1">Operational Role</label>
        <div className="relative">
        <select className="w-full h-11 bg-[#F6F8FC] border border-slate-200 rounded-lg px-4 font-mono text-slate-800 appearance-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all cursor-pointer">
        <option>Incident Commander</option>
        <option>Field Coordinator</option>
        <option>Analyst</option>
        <option>Observer</option>
        </select>
        <span className="material-symbols-outlined absolute right-3 top-2.5 pointer-events-none text-slate-400">keyboard_arrow_down</span>
        </div>
        </div>

        {/* Password Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
        <label className="block text-[12px] font-bold text-slate-600 mb-1.5 ml-1">Password</label>
        <input className="w-full h-11 bg-[#F6F8FC] border border-slate-200 rounded-lg px-4 font-mono text-slate-800 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all placeholder:text-slate-400" placeholder="••••••••" type="password"/>
        </div>
        <div>
        <label className="block text-[12px] font-bold text-slate-600 mb-1.5 ml-1">Confirm</label>
        <input className="w-full h-11 bg-[#F6F8FC] border border-slate-200 rounded-lg px-4 font-mono text-slate-800 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all placeholder:text-slate-400" placeholder="••••••••" type="password"/>
        </div>
        </div>

        {/* Primary Action */}
        <button className="w-full h-12 bg-blue-600 text-white font-bold text-[18px] tracking-tight rounded-lg shadow-md hover:brightness-110 active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-6" type="submit">
        <span className="material-symbols-outlined text-xl">how_to_reg</span>
                                REQUEST ACCESS
                            </button>
        </form>

        {/* Status Note */}
        <div className="mt-8 p-4 bg-[#FFF8E6] border border-[#FFD97A] rounded-lg flex items-start gap-3">
        <span className="material-symbols-outlined text-[#bc4800] mt-0.5">shield_person</span>
        <p className="text-[12px] font-bold text-[#7d2d00] leading-tight">
                                Access requires admin approval. Credentials will be verified against organizational registry.
                            </p>
        </div>
        </div>

        {/* Global Footer */}
        <div className="mt-8 flex justify-between items-center px-2">
        <p className="font-mono text-[12px] text-slate-400">SYSTEM_AUTH_V2.0.4</p>
        <div className="flex gap-4">
        <a className="font-mono text-[12px] text-slate-500 hover:text-blue-600 transition-colors" href="#">HELP</a>
        <a className="font-mono text-[12px] text-slate-500 hover:text-blue-600 transition-colors" href="#">SECURITY</a>
        </div>
        </div>
        </div>
        </main>
        </div>
    );
};

export default Register;
