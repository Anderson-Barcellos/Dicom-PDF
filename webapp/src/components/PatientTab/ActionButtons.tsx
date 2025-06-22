
import { useDicomPdf } from '../../hooks/useDicomPdf';
import StatusIndicator from '../Common/StatusIndicator';
import type { PatientStudy } from '../../types/dicom.types';

interface ActionButtonsProps {
  patientStudy: PatientStudy;
  className?: string;
}

export default function ActionButtons({ patientStudy, className = '' }: ActionButtonsProps) {
  const { processStudy, status } = useDicomPdf();

  const handleDownloadPDF = async () => {
    try {
      if (patientStudy.dicomPdfStatus === 'completed' && patientStudy.dicomPdfUrl) {
        // Direct download if PDF is ready
        const link = document.createElement('a');
        link.href = patientStudy.dicomPdfUrl;
        link.download = `${patientStudy.patientName.replace(/\s+/g, '_')}_${patientStudy.studyDate}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Process and then download
        const pdfUrl = await processStudy(patientStudy);
        if (pdfUrl) {
          const link = document.createElement('a');
          link.href = pdfUrl;
          link.download = `${patientStudy.patientName.replace(/\s+/g, '_')}_${patientStudy.studyDate}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    }
  };

  const handleGeneratePDF = async () => {
    try {
      await processStudy(patientStudy);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    }
  };

  const isProcessing = status.isProcessing || patientStudy.dicomPdfStatus === 'processing';
  const isCompleted = patientStudy.dicomPdfStatus === 'completed';
  const hasError = patientStudy.dicomPdfStatus === 'error';

  return (
    <div className={`action-buttons ${className}`}>
      {/* Primary Viewer Actions */}
      <div className="flex gap-4">
        {/* OHIF Viewer */}
        <a
          href={patientStudy.ohifUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="action-button primary"
          title="Open in OHIF Viewer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <span>📁 Open OHIF</span>
        </a>

        {/* Stone Viewer */}
        <a
          href={patientStudy.stoneUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="action-button primary"
          title="Open in Stone Viewer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>🔍 Open Stone</span>
        </a>
      </div>

      {/* PDF Actions */}
      <div className="flex gap-4 items-center">
        {/* PDF Status */}
        <div className="flex items-center gap-2">
          <StatusIndicator status={patientStudy.dicomPdfStatus} size="sm" />
          <span className="text-sm text-blue-200">
            PDF {patientStudy.dicomPdfStatus}
          </span>
        </div>

        {/* Generate PDF Button */}
        {!isCompleted && (
          <button
            onClick={handleGeneratePDF}
            disabled={isProcessing}
            className="action-button success"
            title="Generate PDF Report"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {isProcessing ? (
              <span>Processing...</span>
            ) : hasError ? (
              <span>Retry PDF</span>
            ) : (
              <span>Generate PDF</span>
            )}
          </button>
        )}

        {/* Download PDF Button */}
        <button
          onClick={handleDownloadPDF}
          disabled={isProcessing}
          className="action-button success"
          title="Download PDF Report"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>📥 Download PDF</span>
        </button>
      </div>

      {/* Additional Actions */}
      <div className="flex gap-4">
        {/* Study Archive Download */}
        <button
          onClick={() => {
            // TODO: Implement study archive download via Orthanc API
            console.log('Download study archive for:', patientStudy.id);
          }}
          className="action-button"
          title="Download DICOM Archive"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          <span>Archive</span>
        </button>

        {/* Share/Export */}
        <button
          onClick={() => {
            // TODO: Implement share functionality
            console.log('Share study:', patientStudy.id);
          }}
          className="action-button"
          title="Share Study"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          <span>Share</span>
        </button>

        {/* Study Details */}
        <button
          onClick={() => {
            // TODO: Show detailed study information modal
            console.log('Show study details for:', patientStudy.id);
          }}
          className="action-button"
          title="Study Details"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Details</span>
        </button>
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <div className="flex items-center gap-2 mt-2 p-2 bg-blue-800 bg-opacity-30 rounded border border-blue-500 border-opacity-30">
          <div className="loading-spinner w-4 h-4" />
          <span className="text-sm text-blue-200">
            Processing PDF... This may take a few minutes.
          </span>
          {status.queueStatus && (
            <span className="text-xs text-blue-300 ml-2">
              Queue: {status.queueStatus.pending} pending, {status.queueStatus.processing} processing
            </span>
          )}
        </div>
      )}

      {/* Error Display */}
      {status.error && (
        <div className="flex items-center gap-2 mt-2 p-2 bg-red-800 bg-opacity-30 rounded border border-red-500 border-opacity-30">
          <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span className="text-sm text-red-200">
            Error: {status.error}
          </span>
        </div>
      )}
    </div>
  );
}