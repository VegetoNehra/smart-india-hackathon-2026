import React, { useState, useEffect } from 'react';
import Sidebar from "./components/layout/Sidebar";
import Topbar from "./components/layout/Topbar";
import HeroStatus from "./components/dashboard/HeroStatus";
import RiskMap from "./components/dashboard/RiskMap";
import KPIStrip from "./components/dashboard/KPIStrip";
import ForecastOutlook from "./components/dashboard/ForecastOutlook";
import AdvisoryCard from "./components/dashboard/AdvisoryCard";
import AdvisoryFeed from "./components/dashboard/AdvisoryFeed";
import DeliveryChannels from "./components/dashboard/DeliveryChannels";

// Import Sidebar pages
import MapPage from "./components/pages/MapPage";
import DataSourcesPage from "./components/pages/DataSourcesPage";
import ModelPage from "./components/pages/ModelPage";
import AdvisoryPage from "./components/pages/AdvisoryPage";
import SettingsPage from "./components/pages/SettingsPage";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [regions, setRegions] = useState([]);
  const [selectedStateId, setSelectedStateId] = useState(null);
  const [selectedDistrictId, setSelectedDistrictId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [liveForecast, setLiveForecast] = useState(null);

  // Fetch live geographical context from database
  useEffect(() => {
    fetch("/api/v1/regions")
      .then((res) => res.json())
      .then((data) => {
        setRegions(data);
        const states = data.filter((r) => r.level === "State");
        if (states.length > 0) {
          setSelectedStateId(states[0].id);
          const districts = data.filter((r) => r.level === "District" && r.parent_id === states[0].id);
          if (districts.length > 0) {
            setSelectedDistrictId(districts[0].id);
          }
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load regions globally in App.jsx", err);
        setLoading(false);
      });
  }, []);

  // Fetch live forecast from Phase 7 Production Inference Pipeline whenever state/district selection changes
  useEffect(() => {
    const states = regions.filter((r) => r.level === "State");
    const selectedState = states.find((s) => s.id === selectedStateId);
    const stateName = selectedState ? selectedState.name : "Uttar Pradesh";

    fetch(`/api/v1/forecast/live?state=${encodeURIComponent(stateName)}&prediction_date=2024-06-15&crop_name=Rice&growth_stage=Sowing&soil_moisture_pct=25.0`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "SUCCESS") {
          setLiveForecast(data);
        }
      })
      .catch((err) => console.error("Error fetching live forecast:", err));
  }, [selectedStateId, selectedDistrictId, regions]);

  const handleStateChange = (stateId) => {
    setSelectedStateId(Number(stateId));
    const firstDistrict = regions.find((r) => r.level === "District" && r.parent_id === Number(stateId));
    if (firstDistrict) {
      setSelectedDistrictId(firstDistrict.id);
    } else {
      setSelectedDistrictId(null);
    }
  };

  const handleDistrictChange = (districtId) => {
    setSelectedDistrictId(Number(districtId));
  };

  // Derive selection scopes
  const states = regions.filter((r) => r.level === "State");
  const selectedState = states.find((s) => s.id === selectedStateId) || null;
  const districts = regions.filter((r) => r.level === "State" ? false : r.parent_id === selectedStateId);
  const selectedDistrict = regions.find((d) => d.id === selectedDistrictId) || null;

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-[500px]">
          <div className="font-mono text-violet-500 animate-pulse">Loading live geographical intelligence...</div>
        </div>
      );
    }

    switch (currentPage) {
      case "dashboard":
        return (
          <>
            <Topbar 
              states={states}
              districts={districts}
              selectedStateId={selectedStateId}
              selectedDistrictId={selectedDistrictId}
              onStateChange={handleStateChange}
              onDistrictChange={handleDistrictChange}
            />
            {/* HERO ROW */}
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.35fr] gap-[22px] items-stretch">
              <HeroStatus selectedRegion={selectedDistrict || selectedState} liveForecast={liveForecast} />
              <RiskMap selectedRegion={selectedDistrict || selectedState} />
            </div>
            
            {/* KPI STRIP */}
            <KPIStrip selectedRegion={selectedDistrict || selectedState} liveForecast={liveForecast} />
            
            {/* FORECAST & ADVISORY ROW */}
            <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-[22px] items-stretch">
              <div className="flex flex-col gap-[22px]">
                <AdvisoryCard liveForecast={liveForecast} />
                <ForecastOutlook liveForecast={liveForecast} />
              </div>
              <div className="flex flex-col gap-[22px]">
                <AdvisoryFeed />
                <DeliveryChannels />
              </div>
            </div>
          </>
        );
      case "map":
        return (
          <MapPage 
            selectedStateId={selectedStateId}
            selectedDistrictId={selectedDistrictId}
            onStateChange={handleStateChange}
            onDistrictChange={handleDistrictChange}
          />
        );
      case "data-sources":
        return <DataSourcesPage />;
      case "model":
        return <ModelPage />;
      case "advisory":
        return <AdvisoryPage />;
      case "settings":
        return (
          <SettingsPage 
            states={states}
            districts={districts}
            selectedStateId={selectedStateId}
            selectedDistrictId={selectedDistrictId}
            onStateChange={handleStateChange}
            onDistrictChange={handleDistrictChange}
          />
        );
      default:
        return <div>Page not found</div>;
    }
  };

  return (
    <>
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>
      
      <div className="flex flex-col md:flex-row min-h-screen relative z-10">
        <Sidebar currentPage={currentPage} onPageChange={setCurrentPage} />
        
        <main className="flex-1 flex flex-col px-4 py-4 md:px-[34px] md:py-[26px] pb-24 md:pb-[60px] gap-[22px] max-w-[1400px] mx-auto w-full">
          {renderContent()}
        </main>
      </div>
    </>
  );
}

export default App;
