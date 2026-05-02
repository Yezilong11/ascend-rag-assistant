import { useState, useRef, useEffect } from 'react'
import { Button, Input, Space, Popover, Select, Spin } from 'antd'
import {
  SendOutlined,
  PaperClipOutlined,
  LoadingOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'

const { TextArea } = Input

interface ChatInputProps {
  onSendMessage: (message: string) => void
  onFileUpload?: (file: File) => void
  disabled?: boolean
  isStreaming?: boolean
  availableModels?: Record<string, { name: string; description: string }>
  currentModelKey?: string
  onModelChange?: (modelKey: string) => void
}

export function ChatInput({
  onSendMessage,
  onFileUpload,
  disabled = false,
  isStreaming = false,
  availableModels = {},
  currentModelKey = '',
  onModelChange,
}: ChatInputProps) {
  const [inputValue, setInputValue] = useState('')
  const [uploadOpen, setUploadOpen] = useState(false)
  const textAreaRef = useRef<any>(null)

  useEffect(() => {
    if (!disabled && textAreaRef.current) {
      textAreaRef.current.focus()
    }
  }, [disabled])

  const handleSend = () => {
    if (inputValue.trim() && !disabled && !isStreaming) {
      onSendMessage(inputValue.trim())
      setInputValue('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileChange = (info: { file: UploadFile }) => {
    const file = info.file.originFileObj as File
    if (file && onFileUpload) {
      onFileUpload(file)
      setUploadOpen(false)
    }
  }

  const modelOptions = Object.entries(availableModels).map(([key, model]) => ({
    value: key,
    label: model.name,
  }))

  return (
    <div className="bg-white border-t border-gray-200 p-4 rounded-b-xl">
      <div className="flex items-end gap-3">
        <div className="flex-1">
          <TextArea
            ref={textAreaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="请输入您的问题，按回车发送..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={disabled || isStreaming}
            className="!rounded-xl !border-gray-200 hover:!border-blue-400 focus:!border-blue-500"
          />
        </div>

        <Space>
          {onFileUpload && (
            <Popover
              content={
                <div className="w-64">
                  <input
                    type="file"
                    accept=".pdf,.txt,.md"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) {
                        handleFileChange({ file: file as unknown as UploadFile })
                      }
                    }}
                    className="block w-full text-sm text-gray-500
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-full file:border-0
                      file:text-sm file:font-semibold
                      file:bg-blue-50 file:text-blue-700
                      hover:file:bg-blue-100
                      cursor-pointer"
                  />
                </div>
              }
              title="上传竞赛资料"
              trigger="click"
              open={uploadOpen}
              onOpenChange={setUploadOpen}
            >
              <Button
                icon={<PaperClipOutlined />}
                disabled={disabled || isStreaming}
                className="!rounded-xl"
              >
                上传
              </Button>
            </Popover>
          )}

          {onModelChange && Object.keys(availableModels).length > 0 && (
            <Select
              value={currentModelKey}
              onChange={onModelChange}
              options={modelOptions}
              style={{ width: 140 }}
              disabled={disabled || isStreaming}
              className="!rounded-xl"
            />
          )}

          <Button
            type="primary"
            icon={isStreaming ? <LoadingOutlined /> : <SendOutlined />}
            onClick={handleSend}
            disabled={!inputValue.trim() || disabled || isStreaming}
            className="!rounded-xl !bg-blue-500 !border-blue-500 hover:!bg-blue-600 hover:!border-blue-600"
          >
            {isStreaming ? '生成中' : '发送'}
          </Button>
        </Space>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
        <div>按 Enter 发送，Shift + Enter 换行</div>
        <div>基于 RAG + 大语言模型技术</div>
      </div>
    </div>
  )
}
