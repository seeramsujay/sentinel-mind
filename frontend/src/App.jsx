import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AssetTree from './pages/AssetTree';
import FieldUpload from './pages/FieldUpload';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/assets" element={<AssetTree />} />
        <Route path="/upload" element={<FieldUpload />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
