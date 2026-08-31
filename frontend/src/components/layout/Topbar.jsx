import React, { useState, useEffect } from "react";
import { MapPin } from "lucide-react";
import SearchableSelect from "../common/SearchableSelect";

export default function Topbar({
  states = [],
  districts = [],
  selectedStateId,
  selectedDistrictId,
  onStateChange,
  onDistrictChange
}) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    // Format: Sat, 27 Sep 2024
    const datePart = date.toLocaleDateString("en-IN", {
      weekday: "short",
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
    // Format: 09:00:00
    const timePart = date.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
    return `${datePart} · IST ${timePart}`;
  };

  return (
    <div className="flex items-center justify-between gap-5 flex-wrap">
      <div>
        <div className="font-mono text-[11.5px] tracking-[.16em] text-teal-500 uppercase mb-1.5 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-500 shadow-[0_0_10px_#0891b2] animate-pulse"></span>
          Monsoon Intelligence · Live Model
        </div>
        <h1 className="font-display font-semibold text-[27px] tracking-[-0.01em] text-text-hi">
          National Advisory Overview
        </h1>
      </div>
      
      <div className="flex items-center gap-4.5">
        {/* State selection searchable dropdown */}
        <div className="flex items-center gap-2">
          <MapPin size={14} className="text-violet-500 shrink-0" />
          <SearchableSelect 
            options={states}
            value={selectedStateId}
            onChange={onStateChange}
            placeholder="Select State"
          />
        </div>

        {/* District selection searchable dropdown */}
        <SearchableSelect 
          options={districts}
          value={selectedDistrictId}
          onChange={onDistrictChange}
          placeholder="Select District"
        />

        <div className="bg-glass-fill border border-glass-borderSoft backdrop-blur-[20px] rounded-full py-2.5 px-4.5 text-[13.5px] text-text-mid font-sans flex items-center h-full">
          {formatTime(time)}
        </div>
      </div>
    </div>
  );
}
