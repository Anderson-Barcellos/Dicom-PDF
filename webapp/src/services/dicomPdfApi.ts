import axios from 'axios';
import type { PatientStudy, BiometricMeasurement } from '../types/dicom.types';

const DICOM_PDF_BASE_URL = import.meta.env.REACT_APP_DICOM_PDF_URL || 'http://localhost:8000';

// Create axios instance
const dicomPdfApi = axios.create({
  baseURL: DICOM_PDF_BASE_URL,
  timeout: 30000, // 30 seconds for PDF processing
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ProcessingStatus {
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress?: number;
  message?: string;
  pdfUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProcessingRequest {
  patientId: string;
  studyInstanceUID: string;
  studyId: string;
  options?: {
    includeImages?: boolean;
    includeReport?: boolean;
    a4Layout?: boolean;
  };
}

export interface ProcessingResponse {
  jobId: string;
  status: ProcessingStatus;
  estimatedDuration?: number;
}

export interface ReportData {
  history: string;
  findings: string[];
  impression: string;
  measurements?: BiometricMeasurement[];
  generatedAt: string;
}

class DicomPdfApiService {
  // Submit processing request
  async submitProcessingRequest(request: ProcessingRequest): Promise<ProcessingResponse> {
    try {
      const response = await dicomPdfApi.post('/process', {
        ...request,
        options: {
          includeImages: true,
          includeReport: true,
          a4Layout: true,
          ...request.options,
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Error submitting processing request:', error);
      throw new Error('Failed to submit PDF processing request');
    }
  }

  // Get processing status
  async getProcessingStatus(jobId: string): Promise<ProcessingStatus> {
    try {
      const response = await dicomPdfApi.get(`/status/${jobId}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting processing status for job ${jobId}:`, error);
      throw new Error('Failed to get processing status');
    }
  }

  // Download generated PDF
  async downloadPdf(jobId: string): Promise<Blob> {
    try {
      const response = await dicomPdfApi.get(`/download/${jobId}`, {
        responseType: 'blob',
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error downloading PDF for job ${jobId}:`, error);
      throw new Error('Failed to download PDF');
    }
  }

  // Get PDF URL (if available)
  async getPdfUrl(jobId: string): Promise<string> {
    try {
      const response = await dicomPdfApi.get(`/url/${jobId}`);
      return response.data.url;
    } catch (error) {
      console.error(`Error getting PDF URL for job ${jobId}:`, error);
      throw new Error('Failed to get PDF URL');
    }
  }

  // Extract report data from study
  async extractReportData(studyId: string): Promise<ReportData | null> {
    try {
      const response = await dicomPdfApi.post('/extract-report', {
        studyId,
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error extracting report data for study ${studyId}:`, error);
      // Return null instead of throwing to handle studies without reports gracefully
      return null;
    }
  }

  // Get all processing jobs for a patient
  async getPatientJobs(patientId: string): Promise<ProcessingResponse[]> {
    try {
      const response = await dicomPdfApi.get(`/jobs/patient/${patientId}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting jobs for patient ${patientId}:`, error);
      throw new Error('Failed to get patient processing jobs');
    }
  }

  // Cancel processing job
  async cancelJob(jobId: string): Promise<void> {
    try {
      await dicomPdfApi.delete(`/jobs/${jobId}`);
    } catch (error) {
      console.error(`Error canceling job ${jobId}:`, error);
      throw new Error('Failed to cancel processing job');
    }
  }

  // Get processing queue status
  async getQueueStatus(): Promise<{
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  }> {
    try {
      const response = await dicomPdfApi.get('/queue/status');
      return response.data;
    } catch (error) {
      console.error('Error getting queue status:', error);
      throw new Error('Failed to get queue status');
    }
  }

  // Helper: Process patient study and update store
  async processPatientStudy(
    patientStudy: PatientStudy,
    updateCallback?: (status: ProcessingStatus) => void
  ): Promise<string> {
    try {
      // Submit processing request
      const request: ProcessingRequest = {
        patientId: patientStudy.patientId,
        studyInstanceUID: patientStudy.id.split('-')[1] || patientStudy.id,
        studyId: patientStudy.id,
        options: {
          includeImages: true,
          includeReport: true,
          a4Layout: true,
        },
      };

      const response = await this.submitProcessingRequest(request);
      const jobId = response.jobId;

      // Start polling for status updates
      this.pollProcessingStatus(jobId, updateCallback);

      return jobId;
    } catch (error) {
      console.error('Error processing patient study:', error);
      throw error;
    }
  }

  // Helper: Poll processing status
  private async pollProcessingStatus(
    jobId: string,
    updateCallback?: (status: ProcessingStatus) => void,
    maxAttempts: number = 60, // 5 minutes with 5-second intervals
    interval: number = 5000
  ): Promise<void> {
    let attempts = 0;

    const poll = async () => {
      try {
        const status = await this.getProcessingStatus(jobId);
        
        if (updateCallback) {
          updateCallback(status);
        }

        // Check if processing is complete
        if (status.status === 'completed' || status.status === 'error') {
          return;
        }

        // Continue polling if not complete and under max attempts
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, interval);
        } else {
          console.warn(`Polling timeout for job ${jobId}`);
          if (updateCallback) {
            updateCallback({
              status: 'error',
              message: 'Processing timeout',
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            });
          }
        }
      } catch (error) {
        console.error(`Error polling status for job ${jobId}:`, error);
        if (updateCallback) {
          updateCallback({
            status: 'error',
            message: 'Status polling failed',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          });
        }
      }
    };

    // Start polling
    setTimeout(poll, interval);
  }

  // Helper: Get cached PDF URL or trigger processing
  async getOrCreatePdf(patientStudy: PatientStudy): Promise<{
    url?: string;
    jobId?: string;
    status: ProcessingStatus['status'];
  }> {
    try {
      // First check if we already have jobs for this patient
      const existingJobs = await this.getPatientJobs(patientStudy.patientId);
      
      // Look for completed job for this study
      const completedJob = existingJobs.find(
        job => job.status.status === 'completed' && 
        job.status.pdfUrl
      );

      if (completedJob && completedJob.status.pdfUrl) {
        return {
          url: completedJob.status.pdfUrl,
          jobId: completedJob.jobId,
          status: 'completed',
        };
      }

      // Look for in-progress job
      const inProgressJob = existingJobs.find(
        job => job.status.status === 'processing' || job.status.status === 'pending'
      );

      if (inProgressJob) {
        return {
          jobId: inProgressJob.jobId,
          status: inProgressJob.status.status,
        };
      }

      // No existing job, create new one
      const jobId = await this.processPatientStudy(patientStudy);
      
      return {
        jobId,
        status: 'pending',
      };
    } catch (error) {
      console.error('Error getting or creating PDF:', error);
      return {
        status: 'error',
      };
    }
  }

  // Check API connection
  async checkConnection(): Promise<boolean> {
    try {
      await dicomPdfApi.get('/health');
      return true;
    } catch (error) {
      console.error('DICOM-PDF API connection failed:', error);
      return false;
    }
  }
}

export const dicomPdfApiService = new DicomPdfApiService();