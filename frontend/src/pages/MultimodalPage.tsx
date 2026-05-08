import React from 'react'
import ImageIngestPanel from '@/components/multimodal/ImageIngestPanel'
import PDFIngestPanel from '@/components/multimodal/PDFIngestPanel'

const MultimodalPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', gap: 20, maxHeight: 'calc(100vh - 112px)', overflowY: 'auto' }}>
      <div style={{ flex: 1, minWidth: 300 }}>
        <ImageIngestPanel />
      </div>
      <div style={{ flex: 1, minWidth: 300 }}>
        <PDFIngestPanel />
      </div>
    </div>
  )
}

export default MultimodalPage
