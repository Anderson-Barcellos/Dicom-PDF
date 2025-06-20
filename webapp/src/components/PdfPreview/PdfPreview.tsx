interface PdfPreviewProps {
  src: string
}

export default function PdfPreview({ src }: PdfPreviewProps) {
  return (
    <div className="p-4 border border-gray-700 rounded-md">
      <img src={src} alt="PDF preview" className="w-full h-auto" />
    </div>
  )
}
