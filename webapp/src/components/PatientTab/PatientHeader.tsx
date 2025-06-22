
import StatusIndicator from '../Common/StatusIndicator';
import type { PatientStudy } from '../../types/dicom.types';

interface PatientHeaderProps {
  patientStudy: PatientStudy;
  className?: string;
}

export default function PatientHeader({ patientStudy, className = '' }: PatientHeaderProps) {
  const formatDate = (dateString: string): string => {
    if (dateString.length === 8) {
      // YYYYMMDD format
      const year = dateString.substring(0, 4);
      const month = dateString.substring(4, 6);
      const day = dateString.substring(6, 8);
      return `${day}/${month}/${year}`;
    }
    return dateString;
  };

  const formatTime = (timeString: string): string => {
    if (timeString.length >= 6) {
      // HHMMSS format
      const hours = timeString.substring(0, 2);
      const minutes = timeString.substring(2, 4);
      const seconds = timeString.substring(4, 6);
      return `${hours}:${minutes}:${seconds}`;
    }
    return timeString;
  };

  return (
    <div className={`patient-header ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Patient Name and ID */}
          <div className="flex items-center gap-3 mb-2">
            <h1 className="patient-name">
              {patientStudy.patientName}
            </h1>
            <span className="text-sm text-blue-300 font-mono">
              ({patientStudy.patientId})
            </span>
            <StatusIndicator 
              status={patientStudy.dicomPdfStatus} 
              size="md"
            />
          </div>

          {/* Study Description */}
          <h2 className="text-lg text-blue-100 mb-3">
            {patientStudy.studyDescription}
          </h2>
        </div>

        {/* Study ID Badge */}
        <div className="text-right">
          <div className="text-xs text-blue-400 mb-1">Study ID</div>
          <div className="font-mono text-sm bg-blue-800 bg-opacity-50 px-2 py-1 rounded">
            {patientStudy.accessionNumber || patientStudy.id}
          </div>
        </div>
      </div>

      {/* Patient Info Grid */}
      <div className="patient-info">
        {/* Date Info */}
        <div className="patient-info-item">
          <svg className="patient-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span>
            <strong>Study Date:</strong> {formatDate(patientStudy.studyDate)}
            {patientStudy.studyTime && (
              <span className="ml-2 text-sm opacity-75">
                {formatTime(patientStudy.studyTime)}
              </span>
            )}
          </span>
        </div>

        {/* Patient Birth Date */}
        {patientStudy.patientBirthDate && (
          <div className="patient-info-item">
            <svg className="patient-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>
              <strong>Birth Date:</strong> {formatDate(patientStudy.patientBirthDate)}
            </span>
          </div>
        )}

        {/* Modality */}
        <div className="patient-info-item">
          <svg className="patient-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <span>
            <strong>Modality:</strong> {patientStudy.modality}
          </span>
        </div>

        {/* Institution */}
        {patientStudy.institutionName && (
          <div className="patient-info-item">
            <svg className="patient-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span>
              <strong>Institution:</strong> {patientStudy.institutionName}
            </span>
          </div>
        )}

        {/* Referring Physician */}
        {patientStudy.referringPhysician && (
          <div className="patient-info-item">
            <svg className="patient-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>
              <strong>Physician:</strong> {patientStudy.referringPhysician}
            </span>
          </div>
        )}

        {/* Study Statistics */}
        <div className="patient-info-item">
          <svg className="patient-info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>
            <strong>Series:</strong> {patientStudy.seriesCount} | 
            <strong className="ml-2">Instances:</strong> {patientStudy.instanceCount}
          </span>
        </div>
      </div>

      {/* Biometric Measurements Summary */}
      {patientStudy.reportData?.measurements && patientStudy.reportData.measurements.length > 0 && (
        <div className="mt-4 p-3 bg-blue-800 bg-opacity-30 rounded-lg border border-blue-500 border-opacity-30">
          <h3 className="text-sm font-medium text-blue-200 mb-2">
            📏 Biometric Measurements Available
          </h3>
          <div className="flex flex-wrap gap-2">
            {patientStudy.reportData.measurements.map((measurement, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-blue-700 bg-opacity-50 rounded text-xs text-blue-100"
              >
                {measurement.type}: {measurement.value} {measurement.unit}
                {measurement.percentile && ` (P${measurement.percentile})`}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}