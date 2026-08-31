import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Search } from "lucide-react";
import clsx from "clsx";

export default function SearchableSelect({ 
  options = [], 
  value, 
  onChange, 
  placeholder = "Select option...", 
  className 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef(null);

  // Find the selected option in the list
  const selectedOption = options.find(opt => String(opt.id) === String(value));

  // Filter options based on search input
  const filteredOptions = options.filter(opt =>
    opt.name.toLowerCase().includes(search.toLowerCase())
  );

  // Close dropdown if clicked outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Reset search filter when dropdown is closed
  useEffect(() => {
    if (!isOpen) {
      setSearch("");
    }
  }, [isOpen]);

  return (
    <div ref={containerRef} className={clsx("relative w-full", className)}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-glass-fill2 border border-glass-borderSoft px-4.5 py-2 text-[13.5px] text-text-hi rounded-full outline-none transition-all duration-200 hover:bg-glass-fill flex justify-between items-center cursor-pointer min-w-[140px]"
      >
        <span className={clsx(!selectedOption && "text-text-lo")}>
          {selectedOption ? selectedOption.name : placeholder}
        </span>
        <ChevronDown size={14} className={clsx("opacity-60 transition-transform ml-2 shrink-0", isOpen && "rotate-180")} />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1.5 bg-[#f0f4f8] border border-glass-borderSoft rounded-2xl shadow-xl overflow-hidden flex flex-col max-h-[220px]">
          {/* Search bar inside dropdown */}
          <div className="flex items-center gap-2 border-b border-glass-borderSoft px-3.5 py-2.5 bg-white/50">
            <Search size={14} className="opacity-50 text-text-hi shrink-0" />
            <input
              type="text"
              placeholder="Type to search..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-transparent border-none outline-none text-[13px] text-text-hi font-sans"
              autoFocus
            />
          </div>

          {/* Option list */}
          <div className="overflow-y-auto flex-1 py-1">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => {
                    onChange(opt.id);
                    setIsOpen(false);
                  }}
                  className={clsx(
                    "w-full text-left px-4.5 py-2 text-[13px] hover:bg-violet-500 hover:text-white cursor-pointer font-sans transition-colors",
                    String(opt.id) === String(value) ? "bg-violet-500/10 text-violet-600 font-semibold" : "text-text-hi"
                  )}
                >
                  {opt.name}
                </button>
              ))
            ) : (
              <div className="px-4.5 py-3 text-[12.5px] text-text-lo font-sans text-center">No results found</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
