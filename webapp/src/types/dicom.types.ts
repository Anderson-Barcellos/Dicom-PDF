export interface Study {
  patientId: string;
  patientName: string;
  alternativeId: string;
  description: string;
  studyDate: string;
  modality: 'CR' | 'DX' | 'US' | 'CT' | 'MR' | 'CRT';
  accessionNumber: string;
  studyInstanceUID: string;
}

export interface MedicalReport {
  history: string;
  findings: string[];
  impression: string;
  studyDetails: {
    studyId: string;
    series: string;
    studyInstanceUID: string;
    referringPhysician?: string;
    institution?: string;
    seriesDescription: string;
    studyDate: string;
  };
}

// Extended interface for the new medical interface
export interface PatientStudy {
  id: string;
  patientId: string;
  patientName: string;
  patientBirthDate: string;
  studyDate: string;
  studyTime: string;
  modality: string;
  studyDescription: string;
  accessionNumber: string;
  seriesCount: number;
  instanceCount: number;
  institutionName?: string;
  referringPhysician?: string;
  
  // URLs para viewers
  ohifUrl: string;
  stoneUrl: string;
  
  // Status do processamento
  dicomPdfStatus: 'pending' | 'processing' | 'completed' | 'error';
  dicomPdfUrl?: string;
  
  // Dados do laudo
  reportData?: {
    history: string;
    findings: string[];
    impression: string;
    measurements?: BiometricMeasurement[];
  };
}

export interface BiometricMeasurement {
  type: 'HC' | 'BPD' | 'AC' | 'FL' | 'EFW';
  value: number;
  unit: string;
  percentile?: number;
  gestationalAge?: number;
}

export interface TabState {
  id: string;
  patientStudy: PatientStudy;
  isActive: boolean;
  isLoading: boolean;
}
