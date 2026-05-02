import { useState } from 'react'
import { Card, Row, Col, Statistic, Progress, Space, Table, Tag, Button, Empty, Spin } from 'antd'
import { DatabaseOutlined, FileOutlined, ClockCircleOutlined, ReloadOutlined } from '@ant-design/icons'
import { FileUploader } from '../components/knowledge/FileUploader'
import type { Document } from '../types'

const mockDocuments: Document[] = [
  {
    id: '1',
    file_name: '中国国际大学生创新大赛-报名须知.pdf',
    file_type: 'pdf',
    doc_type: 'registration',
    uploaded_at: '2024-01-15',
    size: 1024 * 1024 * 2.5,
    chunk_count: 45,
  },
  {
    id: '2',
    file_name: '挑战杯-常见问题FAQ.md',
    file_type: 'md',
    doc_type: 'faq',
    uploaded_at: '2024-01-14',
    size: 1024 * 128,
    chunk_count: 23,
  },
  {
    id: '3',
    file_name: '大唐杯比赛规则.pdf',
    file_type: 'pdf',
    doc_type: 'rules',
    uploaded_at: '2024-01-13',
    size: 1024 * 1024 * 1.8,
    chunk_count: 38,
  },
]

const docTypeLabels: Record<string, string> = {
  registration: '报名须知',
  tech_doc: '技术文档',
  rules: '竞赛规则',
  history: '历史赛题',
  scoring: '评分标准',
  faq: '常见问题',
  unknown: '未知类型',
}

const docTypeColors: Record<string, string> = {
  registration: 'blue',
  tech_doc: 'cyan',
  rules: 'orange',
  history: 'purple',
  scoring: 'green',
  faq: 'gold',
  unknown: 'default',
}

export function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<Document[]>(mockDocuments)
  const [loading, setLoading] = useState(false)

  const totalChunks = documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0)
  const totalSize = documents.reduce((sum, doc) => sum + doc.size, 0)

  const handleUpload = async (file: File) => {
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const newDoc: Document = {
      id: Math.random().toString(36).substring(7),
      file_name: file.name,
      file_type: file.name.split('.').pop() as 'pdf' | 'txt' | 'md',
      doc_type: 'unknown',
      uploaded_at: new Date().toISOString().split('T')[0],
      size: file.size,
      chunk_count: Math.floor(Math.random() * 50) + 10,
    }

    setDocuments((prev) => [newDoc, ...prev])

    return {
      success: true,
      message: `${file.name} 上传成功，已切分为 ${newDoc.chunk_count} 个片段`,
    }
  }

  const columns = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (name: string, record: Document) => (
        <Space>
          <FileOutlined className={record.file_type === 'pdf' ? 'text-red-500' : 'text-blue-500'} />
          <span className="font-medium">{name}</span>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'doc_type',
      key: 'doc_type',
      render: (docType: string) => (
        <Tag color={docTypeColors[docType] || 'default'}>
          {docTypeLabels[docType] || '未知类型'}
        </Tag>
      ),
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (size: number) => {
        if (size < 1024) return `${size} B`
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
        return `${(size / (1024 * 1024)).toFixed(1)} MB`
      },
    },
    {
      title: '文档块',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      render: (count: number) => <Tag color="blue">{count} 块</Tag>,
    },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
    },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">📚 知识库管理</h2>
        <Button icon={<ReloadOutlined />} onClick={() => setLoading(true)}>
          刷新
        </Button>
      </div>

      <Row gutter={16} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card className="!rounded-xl !border-gray-200">
            <Statistic
              title="文档数量"
              value={documents.length}
              prefix={<DatabaseOutlined className="text-blue-500" />}
              valueStyle={{ color: '#3b82f6' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="!rounded-xl !border-gray-200">
            <Statistic
              title="文档块总数"
              value={totalChunks}
              prefix={<FileOutlined className="text-green-500" />}
              valueStyle={{ color: '#10b981' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="!rounded-xl !border-gray-200">
            <Statistic
              title="总大小"
              value={(totalSize / (1024 * 1024)).toFixed(2)}
              suffix="MB"
              prefix={<ClockCircleOutlined className="text-orange-500" />}
              valueStyle={{ color: '#f59e0b' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="!rounded-xl !border-gray-200">
            <div className="py-2">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-500">知识库状态</span>
                <Tag color="success">运行中</Tag>
              </div>
              <Progress percent={100} showInfo={false} strokeColor="#10b981" />
              <p className="text-xs text-gray-400 mt-2">向量数据库正常</p>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={24}>
        <Col xs={24} lg={12}>
          <Card
            title="上传竞赛资料"
            className="!rounded-xl !border-gray-200"
            extra={<Tag>支持 PDF/TXT/MD</Tag>}
          >
            <FileUploader onUpload={handleUpload} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            title="知识库统计"
            className="!rounded-xl !border-gray-200"
          >
            <div className="space-y-4">
              {Object.entries(docTypeLabels).filter(([key]) => key !== 'unknown').map(([key, label]) => {
                const count = documents.filter((d) => d.doc_type === key).length
                const percent = documents.length > 0 ? (count / documents.length) * 100 : 0
                return (
                  <div key={key}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">{label}</span>
                      <span className="font-medium">{count} 个</span>
                    </div>
                    <Progress
                      percent={percent}
                      showInfo={false}
                      strokeColor={{
                        '0%': '#3b82f6',
                        '100%': '#60a5fa',
                      }}
                      trailColor="#e2e8f0"
                      size="small"
                    />
                  </div>
                )
              })}
            </div>
          </Card>
        </Col>
      </Row>

      <Card
        title="文档列表"
        className="!rounded-xl !border-gray-200 mt-6"
      >
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Spin />
          </div>
        ) : documents.length === 0 ? (
          <Empty description="知识库中暂无文档，请上传" />
        ) : (
          <Table
            columns={columns}
            dataSource={documents}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            className="!rounded-lg"
          />
        )}
      </Card>
    </div>
  )
}
