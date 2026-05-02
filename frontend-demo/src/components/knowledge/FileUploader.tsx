import { useState } from 'react'
import { Upload, Button, message, Progress, Space, Typography } from 'antd'
import { UploadOutlined, FileOutlined, CheckCircleOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'

const { Text } = Typography

interface FileUploaderProps {
  onUpload?: (file: File) => Promise<{ success: boolean; message: string }>
  accept?: string
  maxSize?: number
}

export function FileUploader({
  onUpload,
  accept = '.pdf,.txt,.md',
  maxSize = 100,
}: FileUploaderProps) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState<{ name: string; status: 'success' | 'error' }[]>([])

  const handleUpload = async (file: File) => {
    if (file.size > maxSize * 1024 * 1024) {
      message.error(`文件大小不能超过 ${maxSize}MB`)
      return false
    }

    setUploading(true)
    setProgress(0)

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return prev
        }
        return prev + 10
      })
    }, 200)

    try {
      if (onUpload) {
        const result = await onUpload(file)
        clearInterval(progressInterval)
        setProgress(100)

        if (result.success) {
          setUploadedFiles((prev) => [...prev, { name: file.name, status: 'success' }])
          message.success(result.message)
        } else {
          setUploadedFiles((prev) => [...prev, { name: file.name, status: 'error' }])
          message.error(result.message)
        }
      }
    } catch (error) {
      clearInterval(progressInterval)
      message.error('上传失败，请重试')
    } finally {
      setUploading(false)
      setTimeout(() => setProgress(0), 1000)
    }

    return false
  }

  const uploadProps = {
    name: 'file',
    accept,
    showUploadList: false,
    beforeUpload: handleUpload,
  }

  return (
    <div className="space-y-4">
      <Upload.Dragger
        {...uploadProps}
        disabled={uploading}
        className="!rounded-xl !border-2 !border-dashed !border-gray-300 hover:!border-blue-400 transition-colors"
      >
        <div className="py-8">
          <p className="text-4xl text-gray-400 mb-4">
            <UploadOutlined />
          </p>
          <p className="text-base text-gray-600 mb-2">
            点击或拖拽文件上传到知识库
          </p>
          <p className="text-xs text-gray-400">
            支持 PDF、TXT、Markdown 格式，单文件不超过 {maxSize}MB
          </p>
        </div>
      </Upload.Dragger>

      {uploading && (
        <div className="bg-blue-50 rounded-lg p-4">
          <Space direction="vertical" className="w-full">
            <div className="flex items-center justify-between">
              <Text className="text-sm text-blue-600">正在上传...</Text>
              <Text className="text-sm text-blue-600">{progress}%</Text>
            </div>
            <Progress percent={progress} showInfo={false} strokeColor="#3b82f6" />
          </Space>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <Text strong className="text-sm text-gray-700">已上传文件</Text>
          {uploadedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-2"
            >
              <Space>
                <FileOutlined className={file.status === 'success' ? 'text-green-500' : 'text-red-500'} />
                <Text className="text-sm">{file.name}</Text>
              </Space>
              {file.status === 'success' && (
                <CheckCircleOutlined className="text-green-500" />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
