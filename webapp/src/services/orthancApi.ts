import axios from 'axios';
import type { PatientStudy } from '../types/dicom.types';

const ORTHANC_BASE_URL = import.meta.env.REACT_APP_ORTHANC_URL || 'http://localhost:8042';
const OHIF_BASE_URL = import.meta.env.REACT_APP_OHIF_URL || 'http://localhost:3000';
const STONE_BASE_URL = import.meta.env.REACT_APP_STONE_URL || 'http://localhost:3001';

// Create axios instance with default config
const orthancApi = axios.create({
  baseURL: ORTHANC_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add basic auth if credentials are provided
if (import.meta.env.REACT_APP_ORTHANC_USERNAME && import.meta.env.REACT_APP_ORTHANC_PASSWORD) {
  orthancApi.defaults.auth = {
    username: import.meta.env.REACT_APP_ORTHANC_USERNAME,
    password: import.meta.env.REACT_APP_ORTHANC_PASSWORD,
  };
}

export interface OrthancPatient {
  ID: string;
  PatientID: string;
  PatientName: string;
  PatientBirthDate?: string;
  PatientSex?: string;
  Studies: string[];
}

export interface OrthancStudy {
  ID: string;
  PatientID: string;
  StudyInstanceUID: string;
  StudyDate: string;
  StudyTime: string;
  StudyDescription: string;
  AccessionNumber: string;
  ReferringPhysician?: string;
  InstitutionName?: string;
  Modalities: string[];
  Series: string[];
}

export interface OrthancSeries {
  ID: string;
  SeriesInstanceUID: string;
  SeriesDescription: string;
  Modality: string;
  Instances: string[];
}

class OrthancApiService {
  // Get all patients
  async getPatients(): Promise<string[]> {
    try {
      const response = await orthancApi.get('/patients');
      return response.data;
    } catch (error) {
      console.error('Error fetching patients:', error);
      throw new Error('Failed to fetch patients from Orthanc');
    }
  }

  // Get patient details
  async getPatient(patientId: string): Promise<OrthancPatient> {
    try {
      const response = await orthancApi.get(`/patients/${patientId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching patient ${patientId}:`, error);
      throw new Error(`Failed to fetch patient ${patientId}`);
    }
  }

  // Get study details
  async getStudy(studyId: string): Promise<OrthancStudy> {
    try {
      const response = await orthancApi.get(`/studies/${studyId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching study ${studyId}:`, error);
      throw new Error(`Failed to fetch study ${studyId}`);
    }
  }

  // Get series details
  async getSeries(seriesId: string): Promise<OrthancSeries> {
    try {
      const response = await orthancApi.get(`/series/${seriesId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching series ${seriesId}:`, error);
      throw new Error(`Failed to fetch series ${seriesId}`);
    }
  }

  // Get all studies for a patient
  async getStudiesForPatient(patientId: string): Promise<OrthancStudy[]> {
    try {
      const patient = await this.getPatient(patientId);
      const studies = await Promise.all(
        patient.Studies.map(studyId => this.getStudy(studyId))
      );
      return studies;
    } catch (error) {
      console.error(`Error fetching studies for patient ${patientId}:`, error);
      throw new Error(`Failed to fetch studies for patient ${patientId}`);
    }
  }

  // Convert Orthanc data to PatientStudy format
  async convertToPatientStudy(patientId: string, studyId: string): Promise<PatientStudy> {
    try {
      const [patient, study] = await Promise.all([
        this.getPatient(patientId),
        this.getStudy(studyId),
      ]);

      // Get series count and instance count
      const series = await Promise.all(
        study.Series.map(seriesId => this.getSeries(seriesId))
      );
      
      const instanceCount = series.reduce(
        (total, serie) => total + serie.Instances.length, 
        0
      );

      const patientStudy: PatientStudy = {
        id: `${patientId}-${studyId}`,
        patientId: patient.PatientID,
        patientName: patient.PatientName || 'Unknown Patient',
        patientBirthDate: patient.PatientBirthDate || '',
        studyDate: study.StudyDate,
        studyTime: study.StudyTime,
        modality: study.Modalities.join('/'),
        studyDescription: study.StudyDescription || '',
        accessionNumber: study.AccessionNumber || '',
        seriesCount: study.Series.length,
        instanceCount,
        institutionName: study.InstitutionName,
        referringPhysician: study.ReferringPhysician,
        
        // Generate viewer URLs
        ohifUrl: this.generateOHIFUrl(study.StudyInstanceUID),
        stoneUrl: this.generateStoneUrl(study.StudyInstanceUID),
        
        // Initial status
        dicomPdfStatus: 'pending',
      };

      return patientStudy;
    } catch (error) {
      console.error(`Error converting patient study ${patientId}/${studyId}:`, error);
      throw new Error(`Failed to convert patient study data`);
    }
  }

  // Get all patient studies
  async getAllPatientStudies(): Promise<PatientStudy[]> {
    try {
      const patientIds = await this.getPatients();
      const allStudies: PatientStudy[] = [];

      for (const patientId of patientIds) {
        try {
          const studies = await this.getStudiesForPatient(patientId);
          
          for (const study of studies) {
            const patientStudy = await this.convertToPatientStudy(patientId, study.ID);
            allStudies.push(patientStudy);
          }
        } catch (error) {
          console.warn(`Skipping patient ${patientId} due to error:`, error);
        }
      }

      return allStudies;
    } catch (error) {
      console.error('Error fetching all patient studies:', error);
      throw new Error('Failed to fetch patient studies');
    }
  }

  // Generate OHIF viewer URL
  private generateOHIFUrl(studyInstanceUID: string): string {
    const baseUrl = OHIF_BASE_URL;
    const orthancUrl = encodeURIComponent(ORTHANC_BASE_URL);
    return `${baseUrl}/viewer?StudyInstanceUIDs=${studyInstanceUID}&url=${orthancUrl}`;
  }

  // Generate Stone viewer URL
  private generateStoneUrl(studyInstanceUID: string): string {
    const baseUrl = STONE_BASE_URL;
    const orthancUrl = encodeURIComponent(ORTHANC_BASE_URL);
    return `${baseUrl}?study=${studyInstanceUID}&url=${orthancUrl}`;
  }

  // Download study archive
  async downloadStudyArchive(studyId: string): Promise<Blob> {
    try {
      const response = await orthancApi.get(`/studies/${studyId}/archive`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error(`Error downloading study archive ${studyId}:`, error);
      throw new Error(`Failed to download study archive`);
    }
  }

  // Get study preview image
  async getStudyPreviewImage(studyId: string): Promise<string> {
    try {
      const study = await this.getStudy(studyId);
      if (study.Series.length === 0) {
        throw new Error('No series found in study');
      }

      const firstSeries = await this.getSeries(study.Series[0]);
      if (firstSeries.Instances.length === 0) {
        throw new Error('No instances found in series');
      }

      const instanceId = firstSeries.Instances[0];
      const imageUrl = `/instances/${instanceId}/preview`;
      
      return `${ORTHANC_BASE_URL}${imageUrl}`;
    } catch (error) {
      console.error(`Error getting preview image for study ${studyId}:`, error);
      throw new Error(`Failed to get preview image`);
    }
  }

  // Check Orthanc connection
  async checkConnection(): Promise<boolean> {
    try {
      await orthancApi.get('/system');
      return true;
    } catch (error) {
      console.error('Orthanc connection failed:', error);
      return false;
    }
  }
}

export const orthancApiService = new OrthancApiService();