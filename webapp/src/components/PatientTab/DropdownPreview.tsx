import { useState } from 'react';
import ReportPreview from '../A4Preview/ReportPreview';
import ImagePreview from '../A4Preview/ImagePreview';
import PDFViewer from '../A4Preview/PDFViewer';
import type { PatientStudy } from '../../types/dicom.types';

interface DropdownPreviewProps {
  patientStudy: PatientStudy;
  className?: string;
}

export default function DropdownPreview({ patientStudy, className = '' }: DropdownPreviewProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activePreview, setActivePreview] = useState<'report' | 'images' | 'pdf'>('report');

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handlePreviewChange = (preview: 'report' | 'images' | 'pdf') => {
    setActivePreview(preview);
  };

  return (
    <div className={`${className}`}>
      {/* Dropdown Trigger */}
      <button
        onClick={toggleDropdown}
        className="w-full flex items-center justify-between p-4 bg-blue-800 bg-opacity-30 hover:bg-opacity-50 transition-all duration-200 rounded-lg border border-blue-500 border-opacity-30"
      >
        <div className="flex items-center gap-3">
          <svg className="w-6 h-6 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div className="text-left">
            <div className="font-medium text-blue-100">
              A4 Preview & Reports
            </div>
            <div className="text-sm text-blue-300">
              Medical report, DICOM images, and PDF generation
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Status indicators */}
          <div className="flex gap-1">
            <div className={`w-2 h-2 rounded-full ${
              patientStudy.reportData ? 'bg-green-400' : 'bg-gray-400'
            }`} title="Report data available" />
            <div className={`w-2 h-2 rounded-full ${
              patientStudy.instanceCount > 0 ? 'bg-green-400' : 'bg-gray-400'
            }`} title="DICOM images available" />
            <div className={`w-2 h-2 rounded-full ${
              patientStudy.dicomPdfStatus === 'completed' ? 'bg-green-400' :
              patientStudy.dicomPdfStatus === 'processing' ? 'bg-blue-400 animate-pulse' :
              patientStudy.dicomPdfStatus === 'error' ? 'bg-red-400' :
              'bg-yellow-400'
            }`} title={`PDF status: ${patientStudy.dicomPdfStatus}`} />
          </div>
          
          {/* Dropdown arrow */}
          <svg 
            className={`w-5 h-5 text-blue-300 transition-transform duration-200 ${
              isOpen ? 'rotate-180' : ''
            }`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Dropdown Content */}
      <div className={`dropdown-content ${isOpen ? 'open' : ''}`}>
        {isOpen && (
          <div className="dropdown-preview-container">
            {/* Preview Type Selector */}
            <div className="flex gap-2 mb-6 p-1 bg-gray-200 rounded-lg">
              <button
                onClick={() => handlePreviewChange('report')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all ${
                  activePreview === 'report'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                📄 Report A4
              </button>
              
              <button
                onClick={() => handlePreviewChange('images')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all ${
                  activePreview === 'images'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                🖼️ Images A4
              </button>
              
              <button
                onClick={() => handlePreviewChange('pdf')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all ${
                  activePreview === 'pdf'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                📄 PDF View
              </button>
            </div>

            {/* Preview Content */}
            <div className="preview-grid">
              {activePreview === 'report' && (
                <>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Medical Report A4 Layout
                    </h3>
                    <ReportPreview 
                      patientStudy={patientStudy} 
                      scale="desktop"
                    />
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      DICOM Images Grid A4
                    </h3>
                    <ImagePreview 
                      patientStudy={patientStudy} 
                      scale="desktop"
                      maxImages={8}
                    />
                  </div>
                </>
              )}

              {activePreview === 'images' && (
                <div className="col-span-2">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    DICOM Images - A4 Layout Preview
                  </h3>
                  <div className="flex justify-center">
                    <ImagePreview 
                      patientStudy={patientStudy} 
                      scale="desktop"
                      maxImages={8}
                    />
                  </div>
                </div>
              )}

              {activePreview === 'pdf' && (
                <div className="col-span-2">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Generated PDF Document
                  </h3>
                  <div className="flex justify-center">
                    <PDFViewer 
                      patientStudy={patientStudy} 
                      scale={0.4}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Footer Info */}
            <div className="mt-6 pt-4 border-t border-gray-200 text-center">
              <div className="text-sm text-gray-600">
                <p className="mb-2">
                  <strong>A4 Specifications:</strong> 210mm × 297mm (794px × 1123px @ 96dpi)
                </p>
                <div className="flex justify-center gap-6 text-xs">
                  <span>📊 Preview Scale: 40%</span>
                  <span>🖨️ Print Scale: 100%</span>
                  <span>📱 Mobile Scale: 20%</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}