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
