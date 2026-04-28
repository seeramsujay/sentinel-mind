import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();

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
          <button onClick={() => alert('Toggle Notifications')} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 cursor-pointer active:scale-95 transition-all relative">
            <span className="material-symbols-outlined text-[22px]">notifications</span>
            <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
          <button onClick={() => alert('Settings Menu')} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 cursor-pointer active:scale-95 transition-all">
            <span className="material-symbols-outlined text-[22px]">settings</span>
          </button>
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
