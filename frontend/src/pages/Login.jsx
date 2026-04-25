import React from 'react';
import { Link } from 'react-router-dom';

const Login = () => {
    return (
        <div className="bg-surface-container-low font-body-prose overflow-hidden h-screen flex">
        {/* LEFT HALF: TACTICAL VISUALIZATION (60vw) */}
        <div className="hidden lg:flex w-[60vw] h-full bg-gradient-to-br from-[#0D1B2E] to-[#1A2E50] relative overflow-hidden items-center justify-center border-r border-slate-800">
        
        {/* Large Background Watermark */}
        <div className="absolute flex items-center justify-center opacity-[0.12] pointer-events-none">
        <svg className="w-[800px] h-[800px] text-white" fill="currentColor" viewBox="0 0 100 100">
        <path d="M50 0L93.3 25V75L50 100L6.7 75V25L50 0Z"></path>
        </svg>
        </div>
        {/* Tactical Map Elements */}
        <div className="relative w-full h-full p-24">
        {/* Mock Route Lines (SVG) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 1000 1000">
        <path className="opacity-30" d="M200 300 Q 400 250 600 450 T 800 600" fill="none" stroke="white" strokeDasharray="8,8" strokeWidth="1.5"></path>
        <path className="opacity-20" d="M150 700 Q 450 650 500 200" fill="none" stroke="white" strokeDasharray="4,4" strokeWidth="1"></path>
        <path className="opacity-25" d="M700 100 Q 800 400 300 800" fill="none" stroke="white" strokeDasharray="6,6" strokeWidth="1.2"></path>
        </svg>
        {/* Incident Markers (Animated) */}
        <div className="absolute top-[30%] left-[20%]">
        <div className="w-3 h-3 bg-white rounded-full relative">
        <div className="absolute border-2 border-white/40 rounded-full animate-ping w-12 h-12 -top-4 -left-4"></div>
        </div>
        </div>
        <div className="absolute top-[45%] left-[60%]">
        <div className="w-3 h-3 bg-white rounded-full relative">
        <div className="absolute border-2 border-white/40 rounded-full animate-ping w-16 h-16 -top-6 -left-6"></div>
        </div>
        </div>
        {/* Brand Lockup (Bottom Left) */}
        <div className="absolute bottom-12 left-12 flex flex-col gap-2">
        <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-white flex items-center justify-center rounded-lg" style={{clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)"}}>
        <span className="material-symbols-outlined text-primary text-2xl" data-weight="fill">shield_with_heart</span>
        </div>
        <span className="font-display-brand text-[24px] font-extrabold text-white tracking-widest uppercase">SENTINELMIND</span>
        </div>
        <p className="text-slate-400 font-body-prose ml-[52px]">Orchestrating calm from chaos</p>
        </div>
        </div>
        </div>

        {/* RIGHT HALF: AUTHENTICATION CANVAS (40vw) */}
        <div className="w-full lg:w-[40vw] h-full bg-[#EEF2F7] flex items-center justify-center p-8">
        <div className="w-full max-w-[440px] bg-white rounded-xl shadow-lg border border-[#DDE3EE] p-10 transition-all duration-300 border-2">
        {/* Header */}
        <div className="flex flex-col items-center mb-8">
        <div className="w-14 h-14 bg-blue-600 text-white flex items-center justify-center mb-4" style={{clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)"}}>
        <span className="material-symbols-outlined text-3xl" data-weight="fill">hub</span>
        </div>
        <h1 className="text-[24px] font-extrabold text-[#191b23]">SENTINELMIND</h1>
        </div>

        {/* Tab Switcher */}
        <div className="flex p-1 bg-[#ededf9] rounded-full mb-8">
        <button className="flex-1 py-2 px-4 rounded-full bg-blue-600 text-white text-[12px] font-bold transition-all">
                            SIGN IN
                        </button>
        <Link to="/register" className="flex-1 py-2 px-4 text-center rounded-full text-slate-500 text-[12px] font-bold hover:text-slate-800 transition-all">
                            CREATE ACCOUNT
                        </Link>
        </div>

        {/* Form */}
        <form className="space-y-6">
        {/* Email Field */}
        <div className="space-y-1.5">
        <label className="text-[9px] font-bold text-slate-500 tracking-widest flex items-center gap-2">
        <span className="material-symbols-outlined text-[14px]">mail</span>
                                EMAIL ADDRESS
                            </label>
        <div className="relative group">
        <input className="w-full h-12 bg-slate-50 border border-slate-200 rounded-lg px-4 font-mono text-[13px] focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all" placeholder="name@organization.com" type="email"/>
        </div>
        </div>

        {/* Password Field */}
        <div className="space-y-1.5">
        <label className="text-[9px] font-bold text-slate-500 tracking-widest flex items-center gap-2">
        <span className="material-symbols-outlined text-[14px]">lock</span>
                                PASSWORD
                            </label>
        <div className="relative group">
        <input className="w-full h-12 bg-slate-50 border border-slate-200 rounded-lg px-4 font-mono text-[13px] focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all" placeholder="••••••••••••" type="password"/>
        </div>
        </div>

        {/* Extras */}
        <div className="flex items-center justify-between">
        <label className="flex items-center gap-3 cursor-pointer group">
        <div className="relative">
        <input className="sr-only peer" type="checkbox"/>
        <div className="w-10 h-5 bg-slate-200 rounded-full peer-checked:bg-blue-600 transition-all"></div>
        <div className="absolute top-1 left-1 w-3 h-3 bg-white rounded-full transition-all peer-checked:translate-x-5"></div>
        </div>
        <span className="text-[13px] text-slate-600 group-hover:text-slate-800">Remember this device</span>
        </label>
        <a className="text-[13px] text-slate-500 hover:text-blue-600 transition-colors" href="#">Forgot password?</a>
        </div>

        {/* Primary Action */}
        <Link to="/dashboard" className="w-full h-14 bg-blue-600 text-white font-bold text-[18px] rounded-xl shadow-md hover:shadow-lg hover:bg-blue-700 active:scale-[0.98] transition-all flex items-center justify-center gap-3 w-full block">    
            ACCESS COMMAND CENTER
            <span className="material-symbols-outlined text-xl">arrow_forward</span>
        </Link>
        </form>

        {/* Footer Meta */}
        <div className="mt-8 pt-6 border-t border-slate-200 flex flex-col items-center gap-4">
        <p className="text-[12px] text-slate-500 text-center">
                            Authorized personnel only. All access and activities are logged in the 
                            <span className="font-mono text-[11px] text-slate-600 ml-1">SEC_OPS_LOGGER</span>.
                        </p>
        <div className="flex items-center gap-4">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
        <span className="font-mono text-[10px] text-slate-400 uppercase tracking-tighter">System Health: Nominal</span>
        </div>
        </div>
        </div>
        </div>
        </div>
    );
};

export default Login;
