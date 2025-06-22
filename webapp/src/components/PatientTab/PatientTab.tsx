
import ErrorBoundary from '../Common/ErrorBoundary';
import PatientHeader from './PatientHeader';
import DropdownPreview from './DropdownPreview';
import ActionButtons from './ActionButtons';
import type { PatientStudy } from '../../types/dicom.types';

interface PatientTabProps {
  patientStudy: PatientStudy;
  className?: string;
}

export default function PatientTab({ patientStudy, className = '' }: PatientTabProps) {
  return (
    <ErrorBoundary>
      <div className={`space-y-6 ${className}`}>
        {/* Patient Header */}
        <PatientHeader patientStudy={patientStudy} />

        {/* A4 Preview Dropdown */}
        <DropdownPreview patientStudy={patientStudy} />

        {/* Action Buttons */}
        <ActionButtons patientStudy={patientStudy} />
      </div>
    </ErrorBoundary>
  );
}