import { multimodalApiClient } from './api'
import type { ImageIngestResponse, PDFIngestResponse, MultimodalProcessingStatus } from '@/types/multimodal'

export const multimodalApi = {
  ingestImage: async (
    files: File[],
    documentType: string = 'unknown',
    vlmEnabled: boolean = false,
  ): Promise<ImageIngestResponse> => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    formData.append('document_type', documentType)
    formData.append('vlm_enabled', String(vlmEnabled))
    const { data } = await multimodalApiClient.post<ImageIngestResponse>(
      '/image/ingest',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return data
  },

  ingestPdf: async (
    file: File,
    documentType: string = 'unknown',
    extractImages: boolean = true,
    vlmEnabled: boolean = false,
  ): Promise<PDFIngestResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('document_type', documentType)
    formData.append('extract_images', String(extractImages))
    formData.append('vlm_enabled', String(vlmEnabled))
    const { data } = await multimodalApiClient.post<PDFIngestResponse>(
      '/pdf/ingest',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    return data
  },

  deleteBySource: async (sourceFile: string): Promise<{ deleted_count: number }> => {
    const { data } = await multimodalApiClient.delete<{ deleted_count: number }>(
      `/source/${encodeURIComponent(sourceFile)}`,
    )
    return data
  },

  getStatus: async (sourceFile: string): Promise<MultimodalProcessingStatus> => {
    const { data } = await multimodalApiClient.get<MultimodalProcessingStatus>(
      `/status/${encodeURIComponent(sourceFile)}`,
    )
    return data
  },
}
