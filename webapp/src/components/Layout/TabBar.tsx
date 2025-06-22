import React, { useState } from 'react';
import { useTabManager } from '../../hooks/useTabManager';
import { usePatientStore } from '../../stores/patientStore';
import type { PatientStudy } from '../../types/dicom.types';

interface TabBarProps {
  className?: string;
  onAddTabClick?: () => void;
}

export default function TabBar({ className = '', onAddTabClick }: TabBarProps) {
  const { 
    tabs, 
    activeTabId, 
    switchToTab, 
    closeTab, 
    getTabTitle, 
    getTabSubtitle 
  } = useTabManager();
  
  const { patients } = usePatientStore();
  const [showPatientDropdown, setShowPatientDropdown] = useState(false);

  const handleTabClick = (tabId: string) => {
    switchToTab(tabId);
  };

  const handleTabClose = (e: React.MouseEvent, tabId: string) => {
    e.stopPropagation();
    closeTab(tabId);
  };

  const handleAddTab = () => {
    if (onAddTabClick) {
      onAddTabClick();
    } else {
      setShowPatientDropdown(!showPatientDropdown);
    }
  };

  const handlePatientSelect = (patient: PatientStudy) => {
    const { openTab } = useTabManager();
    openTab(patient);
    setShowPatientDropdown(false);
  };

  return (
    <div className={`tab-bar ${className}`}>
      {/* Render existing tabs */}
      {tabs.map((tab) => (
        <div
          key={tab.id}
          className={`tab-item ${tab.isActive ? 'active' : ''}`}
          onClick={() => handleTabClick(tab.id)}
        >
          <div className="flex items-center gap-2">
            {/* Tab Content */}
            <div className="flex flex-col min-w-0">
              <div className="font-medium text-sm truncate">
                {getTabTitle(tab)}
              </div>
              <div className="text-xs text-blue-200 truncate">
                {getTabSubtitle(tab)}
              </div>
            </div>

            {/* Loading Indicator */}
            {tab.isLoading && (
              <div className="loading-spinner w-3 h-3" />
            )}

            {/* Status Indicator */}
            <div className={`w-2 h-2 rounded-full ${
              tab.patientStudy.dicomPdfStatus === 'completed' ? 'bg-green-400' :
              tab.patientStudy.dicomPdfStatus === 'processing' ? 'bg-blue-400 animate-pulse' :
              tab.patientStudy.dicomPdfStatus === 'error' ? 'bg-red-400' :
              'bg-yellow-400'
            }`} />
          </div>

          {/* Tab Dropdown Trigger */}
          <button
            className="tab-dropdown-trigger"
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Show tab-specific dropdown menu
              console.log('Tab dropdown for:', tab.patientStudy.patientName);
            }}
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Close Button */}
          <button
            className="ml-1 p-1 rounded hover:bg-white hover:bg-opacity-20 transition-colors"
            onClick={(e) => handleTabClose(e, tab.id)}
            title="Close tab"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}

      {/* Add New Tab Button */}
      <div className="relative">
        <button
          className="tab-add-button"
          onClick={handleAddTab}
          title="Open new patient tab"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>

        {/* Patient Selection Dropdown */}
        {showPatientDropdown && (
          <div className="absolute top-full left-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
            <div className="p-3 border-b border-gray-100">
              <h3 className="font-medium text-gray-900">Select Patient</h3>
              <p className="text-sm text-gray-500">Choose a patient to open in new tab</p>
            </div>
            
            <div className="max-h-72 overflow-y-auto">
              {patients.length === 0 ? (
                <div className="p-4 text-center text-gray-500">
                  No patients available
                </div>
              ) : (
                patients.map((patient) => (
                  <button
                    key={patient.id}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-b-0"
                    onClick={() => handlePatientSelect(patient)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 truncate">
                          {patient.patientName}
                        </div>
                        <div className="text-sm text-gray-500 truncate">
                          {patient.patientId} • {patient.studyDate} • {patient.modality}
                        </div>
                        <div className="text-xs text-gray-400 truncate">
                          {patient.studyDescription}
                        </div>
                      </div>
                      
                      <div className="ml-2 flex items-center gap-2">
                        {/* PDF Status */}
                        <div className={`w-2 h-2 rounded-full ${
                          patient.dicomPdfStatus === 'completed' ? 'bg-green-400' :
                          patient.dicomPdfStatus === 'processing' ? 'bg-blue-400' :
                          patient.dicomPdfStatus === 'error' ? 'bg-red-400' :
                          'bg-yellow-400'
                        }`} />
                        
                        {/* Arrow */}
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
            
            {patients.length > 0 && (
              <div className="p-3 border-t border-gray-100 bg-gray-50">
                <div className="text-xs text-gray-500">
                  {patients.length} {patients.length === 1 ? 'patient' : 'patients'} available
                </div>
              </div>
            )}
          </div>
        )}

        {/* Backdrop for dropdown */}
        {showPatientDropdown && (
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setShowPatientDropdown(false)}
          />
        )}
      </div>

      {/* Tab Navigation Hints */}
      {tabs.length > 1 && (
        <div className="ml-4 text-xs text-blue-300 opacity-70">
          Ctrl+Tab to navigate • Ctrl+W to close
        </div>
      )}
    </div>
  );
}