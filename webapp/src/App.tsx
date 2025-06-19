import StudyList from './components/StudyList/StudyList'
import DicomViewer from './components/DicomViewer/DicomViewer'
import MedicalReportView from './components/MedicalReport/MedicalReport'
import type { Study, MedicalReport } from './types/dicom.types'

const mockStudies: Study[] = [
  {
    patientId: '001',
    patientName: 'Fulano',
    alternativeId: 'ALT001',
    description: 'US Abdomen',
    studyDate: '20240619',
    modality: 'US',
    accessionNumber: 'ACC001',
    studyInstanceUID: '1.2.3.4.5'
  }
]

const mockReport: MedicalReport = {
  history: 'Paciente sem antecedentes',
  findings: ['Nenhuma alteração significativa'],
  impression: 'Exame normal',
  studyDetails: {
    studyId: '001',
    series: '1',
    studyInstanceUID: '1.2.3.4.5',
    seriesDescription: 'Serie 1',
    studyDate: '20240619'
  }
}

function App() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 text-white bg-gray-800 min-h-screen">
      <StudyList studies={mockStudies} />
      <DicomViewer />
      <MedicalReportView report={mockReport} />
    </div>
  )
}

export default App
