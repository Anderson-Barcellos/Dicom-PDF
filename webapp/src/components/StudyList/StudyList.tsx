import { useState } from 'react'
import type { Study, MedicalReport } from '../../types/dicom.types'
import PdfPreview from '../PdfPreview/PdfPreview'
import MedicalReportView from '../MedicalReport/MedicalReport'

interface StudyListProps {
  studies: Study[]

  report: MedicalReport

  selected: Study | null
  onSelect: (study: Study) => void

}
export default function StudyList({ studies, report }: StudyListProps) {
  const [expanded, setExpanded] = useState<string | null>(null)

  const toggle = (uid: string) => {
    setExpanded((prev) => (prev === uid ? null : uid))
  }



export default function StudyList({ studies, selected, onSelect }: StudyListProps) {

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-2">Estudos</h2>
      <ul className="divide-y divide-gray-700">
        {studies.map((study) => (

          <li key={study.studyInstanceUID} className="py-2">
            <button
              type="button"
              className="w-full text-left"
              onClick={() => toggle(study.studyInstanceUID)}
            >
              <span className="font-mono text-sm mr-2">{study.patientId}</span>
              {study.patientName} - {study.studyDate} - {study.modality}
            </button>
            {expanded === study.studyInstanceUID && (
              <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                <PdfPreview />
                <MedicalReportView report={report} />
              </div>
            )}

          <li
            key={study.studyInstanceUID}
            className={`py-2 cursor-pointer ${
              selected?.studyInstanceUID === study.studyInstanceUID ? 'font-bold' : ''
            }`}
            onClick={() => onSelect(study)}
          >
            <span className="font-mono text-sm mr-2">{study.patientId}</span>
            {study.patientName} - {study.studyDate} - {study.modality}

          </li>
        ))}
      </ul>
    </div>
  )
}
