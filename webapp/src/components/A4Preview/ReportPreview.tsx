
import A4Container from './A4Container';
import type { PatientStudy, BiometricMeasurement } from '../../types/dicom.types';

interface ReportPreviewProps {
  patientStudy: PatientStudy;
  scale?: 'desktop' | 'tablet' | 'mobile' | 'print';
  className?: string;
}

export default function ReportPreview({ 
  patientStudy, 
  scale = 'desktop',
  className = '' 
}: ReportPreviewProps) {
  const { reportData } = patientStudy;

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

  const formatMeasurement = (measurement: BiometricMeasurement): string => {
    let result = `${measurement.value} ${measurement.unit}`;
    if (measurement.percentile) {
      result += ` (P${measurement.percentile})`;
    }
    if (measurement.gestationalAge) {
      result += ` - ${measurement.gestationalAge}w`;
    }
    return result;
  };

  return (
    <A4Container scale={scale} className={className}>
      <div className="a4-report">
        {/* Header */}
        <div className="a4-report-header">
          <h1>RELATÓRIO MÉDICO</h1>
          <div className="text-center text-sm">
            {patientStudy.institutionName || 'Instituição Médica'}
          </div>
        </div>

        {/* Patient Information */}
        <div className="a4-report-patient-info">
          <div>
            <strong>Paciente:</strong> {patientStudy.patientName}<br />
            <strong>ID:</strong> {patientStudy.patientId}<br />
            <strong>Data Nascimento:</strong> {formatDate(patientStudy.patientBirthDate)}
          </div>
          <div>
            <strong>Data do Estudo:</strong> {formatDate(patientStudy.studyDate)}<br />
            <strong>Modalidade:</strong> {patientStudy.modality}<br />
            <strong>Nº Acesso:</strong> {patientStudy.accessionNumber}
          </div>
        </div>

        {/* Study Details */}
        <div className="a4-report-section">
          <h3>Descrição do Estudo</h3>
          <p>{patientStudy.studyDescription}</p>
          {patientStudy.referringPhysician && (
            <p><strong>Médico Solicitante:</strong> {patientStudy.referringPhysician}</p>
          )}
        </div>

        {/* History */}
        {reportData?.history && (
          <div className="a4-report-section">
            <h3>História Clínica</h3>
            <p>{reportData.history}</p>
          </div>
        )}

        {/* Findings */}
        {reportData?.findings && reportData.findings.length > 0 && (
          <div className="a4-report-section">
            <h3>Achados</h3>
            <ul className="list-disc pl-5">
              {reportData.findings.map((finding, index) => (
                <li key={index} className="mb-1">{finding}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Biometric Measurements */}
        {reportData?.measurements && reportData.measurements.length > 0 && (
          <div className="a4-report-section">
            <h3>Medidas Biométricas</h3>
            <div className="a4-report-measurements">
              {reportData.measurements.map((measurement, index) => (
                <div key={index} className="a4-measurement-item">
                  <span><strong>{measurement.type}:</strong></span>
                  <span>{formatMeasurement(measurement)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Impression */}
        {reportData?.impression && (
          <div className="a4-report-section">
            <h3>Impressão Diagnóstica</h3>
            <p>{reportData.impression}</p>
          </div>
        )}

        {/* Study Statistics */}
        <div className="a4-report-section">
          <h3>Estatísticas do Estudo</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Séries:</strong> {patientStudy.seriesCount}
            </div>
            <div>
              <strong>Instâncias:</strong> {patientStudy.instanceCount}
            </div>
            <div>
              <strong>Status PDF:</strong> {patientStudy.dicomPdfStatus}
            </div>
            <div>
              <strong>Data/Hora:</strong> {formatDate(patientStudy.studyDate)} {patientStudy.studyTime}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-auto pt-4 border-t border-gray-400 text-xs text-center">
          <p>Relatório gerado automaticamente pelo sistema DICOM-PDF</p>
          <p>Data de geração: {new Date().toLocaleString('pt-BR')}</p>
        </div>
      </div>
    </A4Container>
  );
}