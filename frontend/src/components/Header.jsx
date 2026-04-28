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
    <header className="bg-white dark:bg-slate-900 h-14 border-b border-brand-border w-full fixed top-0 left-0 z-[100] flex justify-between items-center px-4 shadow-sm">
      <div className="flex items-center gap-6">
        <Link to="/dashboard" className="flex items-center gap-2 group">
          <svg className="text-primary transition-transform group-hover:scale-110" fill="none" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="2"></path>
            <path d="M12 6L7 9V15L12 18L17 15V9L12 6Z" fill="currentColor"></path>
          </svg>
          <span className="font-display-brand text-[24px] uppercase font-black tracking-tighter text-slate-900">SENTINELMIND</span>
        </Link>
        <div className="flex items-center gap-3 border-l border-brand-border pl-6">
          <div className="flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-200">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            <span className="font-bold text-[12px] uppercase">OPERATIONAL</span>
          </div>
          <div className="flex gap-2">
            <span onClick={() => navigate('/dashboard?urgency=P1')} className="cursor-pointer bg-error/10 text-error font-bold text-[10px] px-2 py-0.5 rounded border border-error/20 hover:bg-error/20 transition-colors">2 CRITICAL</span>
            <span onClick={() => navigate('/dashboard?urgency=P2')} className="cursor-pointer bg-orange-100 text-orange-800 font-bold text-[10px] px-2 py-0.5 rounded border border-orange-200 hover:bg-orange-200 transition-colors">5 HIGH</span>
            <span onClick={() => navigate('/dashboard?urgency=P3')} className="cursor-pointer bg-slate-100 text-slate-600 font-bold text-[10px] px-2 py-0.5 rounded border border-slate-200 hover:bg-slate-200 transition-colors">12 MED</span>
            {location.search.includes('urgency') && (
              <span onClick={() => navigate('/dashboard')} className="cursor-pointer bg-slate-800 text-white font-bold text-[10px] px-2 py-0.5 rounded border border-slate-700 hover:bg-slate-700 transition-colors">CLEAR FILTER</span>
            )}
          </div>
        </div>
      </div>

      {/* Navigation Tabs (Integrated into Header for consistency) */}
      <nav className="flex items-center gap-1 h-full mx-auto">
        <Link to="/dashboard" className={`px-4 h-14 flex items-center font-bold text-[14px] transition-all border-b-2 ${isActive('/dashboard') ? 'text-primary border-primary' : 'text-slate-400 border-transparent hover:text-slate-600'}`}>Dashboard</Link>
        <Link to="/assets" className={`px-4 h-14 flex items-center font-bold text-[14px] transition-all border-b-2 ${isActive('/assets') ? 'text-primary border-primary' : 'text-slate-400 border-transparent hover:text-slate-600'}`}>Asset Tree</Link>
        <Link to="/upload" className={`px-4 h-14 flex items-center font-bold text-[14px] transition-all border-b-2 ${isActive('/upload') ? 'text-primary border-primary' : 'text-slate-400 border-transparent hover:text-slate-600'}`}>Field Upload</Link>
      </nav>

      <div className="flex items-center gap-4">
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-[18px]">search</span>
          <input 
            onKeyDown={(e) => e.key === 'Enter' && alert(`Searching system for: ${e.target.value}`)}
            className="pl-9 pr-4 py-1.5 bg-slate-50 border border-brand-border rounded text-sm focus:ring-1 focus:ring-primary focus:border-primary transition-all w-64 placeholder:text-slate-400" 
            placeholder="Search system assets..." 
            type="text"
          />
        </div>
        <div className="flex gap-2">
          <button onClick={() => alert('Toggle Notifications')} className="p-2 hover:bg-slate-50 rounded-lg text-slate-500 cursor-pointer active:scale-95 transition-all">
            <span className="material-symbols-outlined">notifications_active</span>
          </button>
          <button onClick={() => alert('Settings Menu')} className="p-2 hover:bg-slate-50 rounded-lg text-slate-500 cursor-pointer active:scale-95 transition-all">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <button onClick={() => alert('Support Portal')} className="p-2 hover:bg-slate-50 rounded-lg text-slate-500 cursor-pointer active:scale-95 transition-all">
            <span className="material-symbols-outlined">help_outline</span>
          </button>
          <button onClick={handleLogout} className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 overflow-hidden ml-2 cursor-pointer hover:ring-2 hover:ring-primary transition-all" title="Sign Out">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuAsMTo8u5ZNM35_TD9n_eQkLZZKxHfSXtogoVmyI3Ur8V3pRjJzG-q6tFpOjIegetEEIThzsylhGfVdgJOW0hstEEJqeeqjd8SqF6f2rJNHg4LkxBFJ0mQ7R9L0da2YT-RzzYon70QZppjlDak6AWtkXJWxhHYz_OYlRejxOirDzZHp6OAJ4twsm7GT2nZaG2NPmQl8e6EMvGMYmFVgsM1WhFCFs8Ky8WX8dZQzEXzqXWbYzb9qaOabOI3bmtbNMqg8g4iY1Ezonow" alt="Profile" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
