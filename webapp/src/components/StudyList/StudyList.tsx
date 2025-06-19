import type { Study } from '../../types/dicom.types'

interface StudyListProps {
  studies: Study[]
}

export default function StudyList({ studies }: StudyListProps) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-2">Estudos</h2>
      <ul className="divide-y divide-gray-700">
        {studies.map((study) => (
          <li key={study.studyInstanceUID} className="py-2">
            <span className="font-mono text-sm mr-2">{study.patientId}</span>
            {study.patientName} - {study.studyDate} - {study.modality}
          </li>
        ))}
      </ul>
    </div>
  )
}
