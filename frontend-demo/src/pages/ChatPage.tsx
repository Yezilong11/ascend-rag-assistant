import { useEffect } from 'react'
import { Card, Button, Space, Tooltip } from 'antd'
import { ClearOutlined, ExportOutlined } from '@ant-design/icons'
import { ChatWindow } from '../components/chat/ChatWindow'
import { ChatInput } from '../components/chat/ChatInput'
import { useChatStore } from '../stores/chatStore'
import { apiService } from '../services/api'

export function ChatPage() {
  const {
    messages,
    isLoading,
    isStreaming,
    availableModels,
    currentModelKey,
    sendMessage,
    clearMessages,
    loadModels,
    setCurrentModelKey,
  } = useChatStore()

  useEffect(() => {
    loadModels()
  }, [])

  const handleFileUpload = async (file: File) => {
    try {
      const response = await apiService.uploadDocument(file)
      return {
        success: response.code === 0,
        message: response.message || '上传失败',
      }
    } catch (error) {
      return {
        success: false,
        message: '上传失败，请重试',
      }
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">💬 智能问答</h2>
        <Space>
          <Tooltip title="导出对话记录">
            <Button icon={<ExportOutlined />}>导出</Button>
          </Tooltip>
          <Tooltip title="清空对话记录">
            <Button
              icon={<ClearOutlined />}
              onClick={clearMessages}
              danger
            >
              清空
            </Button>
          </Tooltip>
        </Space>
      </div>

      <Card className="flex-1 !rounded-xl !border-gray-200 overflow-hidden">
        <div className="flex flex-col h-full">
          <div className="flex-1 overflow-hidden">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              isStreaming={isStreaming}
            />
          </div>

          <ChatInput
            onSendMessage={sendMessage}
            onFileUpload={handleFileUpload}
            disabled={false}
            isStreaming={isStreaming}
            availableModels={availableModels}
            currentModelKey={currentModelKey}
            onModelChange={setCurrentModelKey}
          />
        </div>
      </Card>
    </div>
  )
}
