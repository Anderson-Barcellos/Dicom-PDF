import type { MedicalReport } from '../../types/dicom.types'

interface MedicalReportProps {
  report: MedicalReport
}

export default function MedicalReportView({ report }: MedicalReportProps) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-2">Relatório Médico</h2>
      <p><strong>Histórico:</strong> {report.history}</p>
      <p><strong>Impressão:</strong> {report.impression}</p>
    </div>
  )
}
