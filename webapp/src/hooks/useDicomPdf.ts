import { useState, useCallback, useEffect } from 'react';
import { usePatientStore } from '../stores/patientStore';
import { dicomPdfApiService, type ProcessingStatus } from '../services/dicomPdfApi';
import type { PatientStudy } from '../types/dicom.types';

export interface UseDicomPdfOptions {
  autoProcess?: boolean;
  cacheSize?: number;
}

export interface DicomPdfStatus {
  isProcessing: boolean;
  processingJobs: Map<string, ProcessingStatus>;
  error: string | null;
  queueStatus?: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
}

export function useDicomPdf(options: UseDicomPdfOptions = {}) {
  const { autoProcess = false, cacheSize = 50 } = options;
  
  const { updatePatientStudy } = usePatientStore();
  const [processingJobs, setProcessingJobs] = useState<Map<string, ProcessingStatus>>(new Map());
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queueStatus, setQueueStatus] = useState<DicomPdfStatus['queueStatus']>();
  const [pdfCache, setPdfCache] = useState<Map<string, string>>(new Map());

  // Process a patient study
  const processStudy = useCallback(async (patientStudy: PatientStudy): Promise<string | null> => {
    try {
      setIsProcessing(true);
      setError(null);

      console.log('Starting PDF processing for study:', patientStudy.studyDescription);

      // Update patient study status to processing
      updatePatientStudy(patientStudy.id, { dicomPdfStatus: 'processing' });

      // Check if PDF already exists or get/create processing job
      const result = await dicomPdfApiService.getOrCreatePdf(patientStudy);

      if (result.status === 'completed' && result.url) {
        // PDF is ready
        updatePatientStudy(patientStudy.id, {
          dicomPdfStatus: 'completed',
          dicomPdfUrl: result.url,
        });

        // Cache the URL
        setPdfCache(prev => {
          const newCache = new Map(prev);
          newCache.set(patientStudy.id, result.url!);
          
          // Limit cache size
          if (newCache.size > cacheSize) {
            const firstKey = newCache.keys().next().value;
            if (firstKey) {
              newCache.delete(firstKey);
            }
          }
          
          return newCache;
        });

        console.log('PDF processing completed immediately:', result.url);
        return result.url;
      }

      if (result.jobId) {
        // Monitor processing job
        const statusUpdateCallback = (status: ProcessingStatus) => {
          console.log('PDF processing status update:', status);

          // Update local processing jobs map
          setProcessingJobs(prev => {
            const newMap = new Map(prev);
            newMap.set(result.jobId!, status);
            return newMap;
          });

          // Update patient study based on status
          let dicomPdfStatus: PatientStudy['dicomPdfStatus'];
          switch (status.status) {
            case 'pending':
              dicomPdfStatus = 'pending';
              break;
            case 'processing':
              dicomPdfStatus = 'processing';
              break;
            case 'completed':
              dicomPdfStatus = 'completed';
              break;
            case 'error':
              dicomPdfStatus = 'error';
              break;
            default:
              dicomPdfStatus = 'pending';
          }

          updatePatientStudy(patientStudy.id, {
            dicomPdfStatus,
            dicomPdfUrl: status.pdfUrl,
          });

          // Cache completed PDF
          if (status.status === 'completed' && status.pdfUrl) {
            setPdfCache(prev => {
              const newCache = new Map(prev);
              newCache.set(patientStudy.id, status.pdfUrl!);
              
              if (newCache.size > cacheSize) {
                const firstKey = newCache.keys().next().value;
                if (firstKey) {
                  newCache.delete(firstKey);
                }
              }
              
              return newCache;
            });
          }
        };

        // Start processing and monitoring
        await dicomPdfApiService.processPatientStudy(patientStudy, statusUpdateCallback);
        
        console.log('PDF processing job started:', result.jobId);
        return null; // Will be available later via callback
      }

      throw new Error('Failed to initiate PDF processing');

    } catch (error) {
      console.error('Error processing study:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(errorMessage);
      
      updatePatientStudy(patientStudy.id, { dicomPdfStatus: 'error' });
      
      return null;
    } finally {
      setIsProcessing(false);
    }
  }, [updatePatientStudy, cacheSize]);

  // Download PDF
  const downloadPdf = useCallback(async (jobId: string, filename?: string): Promise<void> => {
    try {
      const blob = await dicomPdfApiService.downloadPdf(jobId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `medical-report-${jobId}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
      
    } catch (error) {
      console.error('Error downloading PDF:', error);
      setError(error instanceof Error ? error.message : 'Failed to download PDF');
    }
  }, []);

  // Get cached PDF URL
  const getCachedPdfUrl = useCallback((studyId: string): string | null => {
    return pdfCache.get(studyId) || null;
  }, [pdfCache]);

  // Cancel processing job
  const cancelProcessing = useCallback(async (jobId: string, studyId: string): Promise<void> => {
    try {
      await dicomPdfApiService.cancelJob(jobId);
      
      // Remove from processing jobs
      setProcessingJobs(prev => {
        const newMap = new Map(prev);
        newMap.delete(jobId);
        return newMap;
      });

      // Update patient study status
      updatePatientStudy(studyId, { dicomPdfStatus: 'pending' });
      
      console.log('Processing job canceled:', jobId);
    } catch (error) {
      console.error('Error canceling job:', error);
      setError(error instanceof Error ? error.message : 'Failed to cancel processing');
    }
  }, [updatePatientStudy]);

  // Get processing status for a study
  const getProcessingStatus = useCallback((studyId: string): ProcessingStatus | null => {
    // Find job by study ID (assuming job ID contains study ID or we track this mapping)
    for (const [jobId, status] of processingJobs) {
      if (jobId.includes(studyId)) {
        return status;
      }
    }
    return null;
  }, [processingJobs]);

  // Refresh queue status
  const refreshQueueStatus = useCallback(async (): Promise<void> => {
    try {
      const status = await dicomPdfApiService.getQueueStatus();
      setQueueStatus(status);
    } catch (error) {
      console.error('Error fetching queue status:', error);
    }
  }, []);

  // Check API connection
  const checkConnection = useCallback(async (): Promise<boolean> => {
    try {
      return await dicomPdfApiService.checkConnection();
    } catch (error) {
      console.error('Error checking DICOM-PDF API connection:', error);
      return false;
    }
  }, []);

  // Auto-process new studies if enabled
  useEffect(() => {
    if (!autoProcess) return;

    // This would need to be integrated with the Orthanc sync hook
    // to automatically process new studies as they come in
    console.log('Auto-processing is enabled');
  }, [autoProcess]);

  // Periodically refresh queue status
  useEffect(() => {
    const interval = setInterval(refreshQueueStatus, 30000); // Every 30 seconds
    refreshQueueStatus(); // Initial load
    
    return () => clearInterval(interval);
  }, [refreshQueueStatus]);

  // Return hook interface
  const status: DicomPdfStatus = {
    isProcessing,
    processingJobs,
    error,
    queueStatus,
  };

  return {
    // Status
    status,
    
    // Actions
    processStudy,
    downloadPdf,
    cancelProcessing,
    getCachedPdfUrl,
    getProcessingStatus,
    refreshQueueStatus,
    checkConnection,
    
    // Utilities
    clearError: () => setError(null),
    clearCache: () => setPdfCache(new Map()),
    
    // Configuration
    options: {
      autoProcess,
      cacheSize,
    },
  };
}