import { useState, useEffect } from 'react';
import { useDicomPdf } from '../../hooks/useDicomPdf';
import LoadingSpinner from '../Common/LoadingSpinner';
import type { PatientStudy } from '../../types/dicom.types';

interface PDFViewerProps {
  patientStudy: PatientStudy;
  scale?: number;
  className?: string;
  width?: number;
  height?: number;
}

export default function PDFViewer({ 
  patientStudy, 
  scale = 0.4,
  className = '',
  width = 794,
  height = 1123
}: PDFViewerProps) {
  const { getCachedPdfUrl, processStudy, status } = useDicomPdf();
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pdfDoc, setPdfDoc] = useState<{ url: string } | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadPdf();
  }, [patientStudy.id, patientStudy.dicomPdfUrl]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadPdf = async () => {
    try {
      setError(null);
      
      // Check if we have a cached URL
      let url = getCachedPdfUrl(patientStudy.id);
      
      // Or use the URL from patient study
      if (!url && patientStudy.dicomPdfUrl) {
        url = patientStudy.dicomPdfUrl;
      }
      
      if (url) {
        setPdfUrl(url);
        await loadPdfDocument(url);
      } else if (patientStudy.dicomPdfStatus === 'pending' || patientStudy.dicomPdfStatus === 'error') {
        // Auto-process if not already processing
        await processPdf();
      }
    } catch (error) {
      console.error('Error loading PDF:', error);
      setError(error instanceof Error ? error.message : 'Failed to load PDF');
    }
  };

  const processPdf = async () => {
    if (isProcessing) return;
    
    try {
      setIsProcessing(true);
      setError(null);
      
      const resultUrl = await processStudy(patientStudy);
      if (resultUrl) {
        setPdfUrl(resultUrl);
        await loadPdfDocument(resultUrl);
      }
    } catch (error) {
      console.error('Error processing PDF:', error);
      setError(error instanceof Error ? error.message : 'Failed to process PDF');
    } finally {
      setIsProcessing(false);
    }
  };

  const loadPdfDocument = async (url: string) => {
    try {
      setIsLoading(true);
      
      // For now, we'll show a preview frame since PDF.js integration requires more setup
      // In a full implementation, you would use PDF.js here:
      // const pdf = await pdfjsLib.getDocument(url).promise;
      // setPdfDoc(pdf);
      // setTotalPages(pdf.numPages);
      
      // Placeholder implementation
      setTotalPages(1);
      setPdfDoc({ url }); // Simplified for demo
    } catch (error) {
      console.error('Error loading PDF document:', error);
      setError('Failed to load PDF document');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handleDownload = () => {
    if (pdfUrl) {
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = `${patientStudy.patientName.replace(/\s+/g, '_')}_${patientStudy.studyDate}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const scaledWidth = width * scale;
  const scaledHeight = height * scale;

  // Show processing state
  if (isProcessing || patientStudy.dicomPdfStatus === 'processing') {
    return (
      <div 
        className={`flex flex-col items-center justify-center border border-gray-300 rounded bg-gray-50 ${className}`}
        style={{ width: scaledWidth, height: scaledHeight }}
      >
        <LoadingSpinner size="lg" message="Generating PDF..." />
        <p className="mt-4 text-sm text-gray-600 text-center">
          Processing DICOM data and generating medical report...
        </p>
        {status.processingJobs.size > 0 && (
          <p className="mt-2 text-xs text-gray-500">
            Queue: {status.queueStatus?.pending || 0} pending, {status.queueStatus?.processing || 0} processing
          </p>
        )}
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div 
        className={`flex flex-col items-center justify-center border border-red-300 rounded bg-red-50 ${className}`}
        style={{ width: scaledWidth, height: scaledHeight }}
      >
        <div className="w-12 h-12 mb-3 text-red-400">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="font-bold text-red-700 mb-2">PDF Error</h3>
        <p className="text-sm text-red-600 text-center mb-4 max-w-sm">{error}</p>
        <button
          onClick={processPdf}
          disabled={isProcessing}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors disabled:opacity-50"
        >
          Retry
        </button>
      </div>
    );
  }

  // Show pending state
  if (!pdfUrl || patientStudy.dicomPdfStatus === 'pending') {
    return (
      <div 
        className={`flex flex-col items-center justify-center border border-yellow-300 rounded bg-yellow-50 ${className}`}
        style={{ width: scaledWidth, height: scaledHeight }}
      >
        <div className="w-12 h-12 mb-3 text-yellow-600">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-full h-full">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="font-bold text-yellow-700 mb-2">PDF Not Ready</h3>
        <p className="text-sm text-yellow-600 text-center mb-4">
          PDF has not been generated yet for this study.
        </p>
        <button
          onClick={processPdf}
          disabled={isProcessing}
          className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors disabled:opacity-50"
        >
          Generate PDF
        </button>
      </div>
    );
  }

  return (
    <div className={`flex flex-col ${className}`}>
      {/* PDF Controls */}
      <div className="flex items-center justify-between p-2 bg-gray-100 border border-gray-300 rounded-t">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage <= 1}
            className="px-2 py-1 text-sm bg-white border border-gray-300 rounded disabled:opacity-50 hover:bg-gray-50"
          >
            ←
          </button>
          <span className="text-sm">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="px-2 py-1 text-sm bg-white border border-gray-300 rounded disabled:opacity-50 hover:bg-gray-50"
          >
            →
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Scale: {Math.round(scale * 100)}%</span>
          <button
            onClick={handleDownload}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Download
          </button>
        </div>
      </div>

      {/* PDF Content */}
      <div 
        className="border border-gray-300 border-t-0 rounded-b bg-white overflow-hidden"
        style={{ width: scaledWidth, height: scaledHeight }}
      >
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <LoadingSpinner size="md" message="Loading PDF..." />
          </div>
        ) : pdfDoc ? (
          // Simplified PDF preview - in real implementation, render PDF page here
          <iframe
            src={`${pdfUrl}#page=${currentPage}&zoom=${scale * 100}`}
            className="w-full h-full border-0"
            title="PDF Preview"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>Unable to display PDF</p>
          </div>
        )}
      </div>
    </div>
  );
}