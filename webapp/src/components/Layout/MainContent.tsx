import React from 'react';
import { useTabManager } from '../../hooks/useTabManager';
import PatientTab from '../PatientTab/PatientTab';

interface MainContentProps {
  className?: string;
}

export default function MainContent({ className = '' }: MainContentProps) {
  const { activePatientStudy, stats } = useTabManager();

  if (!stats.hasActiveTabs) {
    return (
      <main className={`patient-tab-content ${className}`}>
        <div className="flex flex-col items-center justify-center min-h-96 text-center">
          <div className="w-24 h-24 mb-6 opacity-50">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={1.5} 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
              />
            </svg>
          </div>
          
          <h2 className="text-2xl font-bold text-blue-200 mb-4">
            Welcome to Orthanc Medical Dashboard
          </h2>
          
          <p className="text-blue-300 mb-6 max-w-md">
            Select a patient from the tab bar above to view medical reports, DICOM images, 
            and generate PDF documents with A4 layouts.
          </p>
          
          <div className="space-y-3 text-sm text-blue-400">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Real-time synchronization with Orthanc Explorer 2
            </div>
            
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              A4 preview layouts for medical reports
            </div>
            
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Automatic PDF generation and processing
            </div>
            
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Integration with OHIF and Stone viewers
            </div>
          </div>
          
          <div className="mt-8 p-4 bg-blue-900 bg-opacity-30 rounded-lg border border-blue-500 border-opacity-30">
            <p className="text-xs text-blue-300">
              💡 <strong>Tip:</strong> Click the + button in the tab bar to select a patient and get started.
            </p>
          </div>
        </div>
      </main>
    );
  }

  if (!activePatientStudy) {
    return (
      <main className={`patient-tab-content ${className}`}>
        <div className="flex flex-col items-center justify-center min-h-96 text-center">
          <div className="loading-spinner w-8 h-8 mb-4" />
          <p className="text-blue-300">Loading patient data...</p>
        </div>
      </main>
    );
  }

  return (
    <main className={`patient-tab-content ${className}`}>
      <PatientTab patientStudy={activePatientStudy} />
    </main>
  );
}