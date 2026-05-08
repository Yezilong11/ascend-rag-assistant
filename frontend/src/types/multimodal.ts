export interface ImageIngestResponse {
  success: boolean
  total_count: number
  success_count: number
  failed_count: number
  image_chunks: Array<{
    id: string
    page_content: string
    image_path: string
    ocr_text: string
    page_number: number
    source_file: string
    document_type: string
  }>
  errors: string[]
  duration_ms: number
  metadata: Record<string, unknown>
}

export interface PDFIngestResponse {
  success: boolean
  pdf_path: string
  text_chunks_count: number
  image_chunks_count: number
  extracted_images_count: number
  errors: string[]
  duration_ms: number
  metadata: Record<string, unknown>
}

export interface MultimodalProcessingStatus {
  exists: boolean
  total_chunks?: number
  processed?: number
  failed?: number
  pending?: number
}

export interface ImageSourceData {
  chunk_id: string
  image_path: string
  description: string
  ocr_text: string
  source_file: string
  page_number: number
  relevance_score: number
  thumbnail_path: string | null
}

export interface MultimodalQueryResponse {
  query: string
  answer: string
  text_sources: Array<{
    chunk_id: string
    content: string
    source_file: string
    page_number: number
    relevance_score: number
  }>
  image_sources: ImageSourceData[]
  total_sources: number
  confidence: number
  duration_ms: number
  metadata: Record<string, unknown>
}
