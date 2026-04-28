import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);


  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    if (window.confirm("Terminate this session and return to Vision Gateway?")) {
      window.location.href = "/";
    }
  };

  return (
    <header className="bg-white/80 backdrop-blur-md h-14 border-b border-slate-200 w-full fixed top-0 left-0 z-[100] flex justify-between items-center px-6 shadow-sm">
      <div className="flex items-center gap-8">
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="absolute inset-0 bg-slate-200 blur-lg rounded-full group-hover:bg-slate-300 transition-all"></div>
            <svg className="text-black relative transition-transform group-hover:scale-110" fill="none" height="28" viewBox="0 0 24 24" width="28" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="2"></path>
              <path d="M12 6L7 9V15L12 18L17 15V9L12 6Z" fill="currentColor"></path>
            </svg>
          </div>
          <span className="font-display-brand text-[22px] uppercase font-black tracking-[-0.05em] text-black">SENTINELMIND</span>
        </Link>
        <div className="flex items-center gap-4 border-l border-slate-200 pl-8 h-8">
          <div className="flex items-center gap-2 bg-emerald-50 text-emerald-600 px-3 py-1 rounded-md border border-emerald-100">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.3)]"></span>
            <span className="font-bold text-[11px] uppercase tracking-wider">OPERATIONAL</span>
          </div>
          <div className="flex gap-2">
            <span onClick={() => alert('Viewing 2 Critical Alerts')} className="cursor-pointer bg-error/10 text-error font-bold text-[10px] px-2 py-0.5 rounded border border-error/20 hover:bg-error/20 transition-colors">2 CRITICAL</span>
            <span onClick={() => alert('Viewing 5 High Priority Alerts')} className="cursor-pointer bg-orange-100 text-orange-800 font-bold text-[10px] px-2 py-0.5 rounded border border-orange-200 hover:bg-orange-200 transition-colors">5 HIGH</span>
            <span onClick={() => alert('Viewing 12 Medium Priority Alerts')} className="cursor-pointer bg-slate-100 text-slate-600 font-bold text-[10px] px-2 py-0.5 rounded border border-slate-200 hover:bg-slate-200 transition-colors">12 MED</span>
          </div>
        </div>
      </div>

      <nav className="flex items-center gap-2 h-full">
        <Link to="/dashboard" className={`px-5 h-14 flex items-center font-bold text-[13px] uppercase tracking-widest transition-all border-b-2 ${isActive('/dashboard') ? 'text-black border-black bg-slate-50' : 'text-slate-400 border-transparent hover:text-slate-900 hover:bg-slate-50'}`}>Dashboard</Link>
        <Link to="/assets" className={`px-5 h-14 flex items-center font-bold text-[13px] uppercase tracking-widest transition-all border-b-2 ${isActive('/assets') ? 'text-black border-black bg-slate-50' : 'text-slate-400 border-transparent hover:text-slate-900 hover:bg-slate-50'}`}>Asset Tree</Link>
        <Link to="/upload" className={`px-5 h-14 flex items-center font-bold text-[13px] uppercase tracking-widest transition-all border-b-2 ${isActive('/upload') ? 'text-black border-black bg-slate-50' : 'text-slate-400 border-transparent hover:text-slate-900 hover:bg-slate-50'}`}>Field Upload</Link>
      </nav>

      <div className="flex items-center gap-6">
        <div className="relative group">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[18px] group-focus-within:text-black transition-colors">search</span>
          <input
            onKeyDown={(e) => e.key === 'Enter' && alert(`Searching system for: ${e.target.value}`)}
            className="pl-10 pr-4 py-1.5 bg-slate-100 border border-slate-200 rounded-lg text-sm text-slate-900 focus:ring-1 focus:ring-black focus:border-black transition-all w-64 placeholder:text-slate-400 outline-none"
            placeholder="Search system assets..."
            type="text"
          />
        </div>
        <div className="flex gap-1">
          <div className="relative">
            <button onClick={() => {setShowNotifications(!showNotifications); setShowSettings(false);}} className={`p-2 rounded-lg cursor-pointer active:scale-95 transition-all relative ${showNotifications ? 'bg-slate-100 text-blue-600' : 'hover:bg-slate-100 text-slate-500'}`}>
              <span className="material-symbols-outlined text-[22px]">notifications</span>
              <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
            {showNotifications && (
              <div className="absolute top-full right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 z-50 overflow-hidden text-left origin-top-right animate-in fade-in zoom-in-95 duration-200">
                  <div className="p-3 border-b border-slate-100 flex justify-between items-center bg-slate-50/80 backdrop-blur-sm">
                      <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">System Alerts</span>
                      <span className="text-[9px] text-blue-600 font-bold bg-blue-50 px-2 py-0.5 rounded-full cursor-pointer hover:bg-blue-100 transition-colors uppercase">CLEAR</span>
                  </div>
                  <div className="p-2 text-xs max-h-64 overflow-y-auto">
                      <div className="p-3 hover:bg-slate-50 rounded-lg cursor-pointer border-b border-transparent transition-colors group">
                          <span className="font-bold text-error flex items-center gap-2 mb-1 text-[11px]"><span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse"></span> CRITICAL: Sector Alpha Surge</span>
                          <span className="text-slate-500 text-[10px] block leading-snug">Multiple high-priority disaster signals detected in quadrant 4. Requesting immediate verification.</span>
                          <span className="text-slate-400 text-[9px] mt-1 block uppercase font-mono group-hover:text-error transition-colors">2 mins ago</span>
                      </div>
                      <div className="p-3 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors group mt-1">
                          <span className="font-bold text-slate-700 flex items-center gap-2 mb-1 text-[11px]"><span className="material-symbols-outlined text-[12px] text-blue-600">tune</span> SYSTEM: Diagnostic Complete</span>
                          <span className="text-slate-500 text-[10px] block leading-snug">AEGIS-02 thermal imaging subsystem calibration executed successfully.</span>
                          <span className="text-slate-400 text-[9px] mt-1 block uppercase font-mono">14 mins ago</span>
                      </div>
                  </div>
              </div>
            )}
          </div>
          <div className="relative">
            <button onClick={() => {setShowSettings(!showSettings); setShowNotifications(false);}} className={`p-2 rounded-lg cursor-pointer active:scale-95 transition-all ${showSettings ? 'bg-slate-100 text-blue-600' : 'hover:bg-slate-100 text-slate-500'}`}>
              <span className="material-symbols-outlined text-[22px]">settings</span>
            </button>
            {showSettings && (
               <div className="absolute top-full right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-slate-200 z-50 p-2 origin-top-right animate-in fade-in zoom-in-95 duration-200">
                   <button onClick={() => setShowSettings(false)} className="w-full text-left px-3 py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-colors cursor-pointer flex items-center gap-2 mb-1">
                       <span className="material-symbols-outlined text-[16px] opacity-70">account_circle</span> Identity Matrix
                   </button>
                   <button onClick={() => setShowSettings(false)} className="w-full text-left px-3 py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-colors cursor-pointer flex items-center gap-2 mb-1">
                       <span className="material-symbols-outlined text-[16px] opacity-70">admin_panel_settings</span> Access Control
                   </button>
                   <div className="h-px w-full bg-slate-100 my-1"></div>
                   <button onClick={() => setShowSettings(false)} className="w-full text-left px-3 py-2 text-xs font-bold text-slate-500 hover:bg-error/10 hover:text-error rounded-lg transition-colors cursor-pointer flex items-center gap-2">
                       <span className="material-symbols-outlined text-[16px] opacity-70">delete_forever</span> Clear Cache
                   </button>
               </div>
            )}
          </div>
          <button onClick={() => alert('Support Portal')} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 cursor-pointer active:scale-95 transition-all">
            <span className="material-symbols-outlined text-[22px]">help</span>
          </button>
          <button onClick={handleLogout} className="w-9 h-9 rounded-full border border-slate-200 overflow-hidden ml-3 cursor-pointer hover:ring-2 hover:ring-black hover:border-transparent transition-all shadow-sm" title="Sign Out">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAsMTo8u5ZNM35_TD9n_eQkLZZKxHfSXtogoVmyI3Ur8V3pRjJzG-q6tFpOjIegetEEIThzsylhGfVdgJOW0hstEEJqeeqjd8SqF6f2rJNHg4LkxBFJ0mQ7R9L0da2YT-RzzYon70QZppjlDak6AWtkXJWxhHYz_OYlRejxOirDzZHp6OAJ4twsm7GT2nZaG2NPmQl8e6EMvGMYmFVgsM1WhFCFs8Ky8WX8dZQzEXzqXWbYzb9qaOabOI3bmtbNMqg8g4iY1Ezonow" alt="Profile" className="w-full h-full object-cover" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
