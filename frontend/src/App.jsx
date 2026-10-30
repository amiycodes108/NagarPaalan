import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Overview from './pages/Overview';
import DashcamIntelligence from './pages/DashcamIntelligence';
import CivicVision from './pages/CivicVision';
import Complaints from './pages/Complaints';
import InfrastructureRegistry from './pages/InfrastructureRegistry';
import CityMemory from './pages/CityMemory';
import CityMap from './pages/CityMap';
import HotspotAnalysis from './pages/HotspotAnalysis';
import Maintenance from './pages/Maintenance';
import FinancialIntelligence from './pages/FinancialIntelligence';
import ContractorManagement from './pages/ContractorManagement';
import DataModels from './pages/DataModels';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {/* All 13 Unified Platform Modules */}
        <Route path="/" element={<Overview />} />
        <Route path="/dashcam" element={<DashcamIntelligence />} />
        <Route path="/civic-vision" element={<CivicVision />} />
        <Route path="/complaints" element={<Complaints />} />
        <Route path="/infrastructure" element={<InfrastructureRegistry />} />
        <Route path="/city-memory" element={<CityMemory />} />
        <Route path="/city-map" element={<CityMap />} />
        <Route path="/hotspots" element={<HotspotAnalysis />} />
        <Route path="/maintenance" element={<Maintenance />} />
        <Route path="/finances" element={<FinancialIntelligence />} />
        <Route path="/contractors" element={<ContractorManagement />} />
        <Route path="/models" element={<DataModels />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
