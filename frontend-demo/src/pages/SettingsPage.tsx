import { Card, Form, Switch, Select, Slider, InputNumber, Button, Space, Divider, message, Tag, Alert } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'
import { useAppStore } from '../stores/appStore'

export function SettingsPage() {
  const { settings, saveSettings, systemStatus } = useAppStore()
  const [form] = Form.useForm()

  const handleSave = (values: any) => {
    saveSettings({
      theme: values.theme,
      model_config: {
        ...settings.model_config,
        model_key: values.model_key,
        use_reranker: values.use_reranker,
        reranker_top_k: values.reranker_top_k,
        initial_retrieval_k: values.initial_retrieval_k,
      },
    })
    message.success('设置已保存')
  }

  const handleReset = () => {
    form.setFieldsValue({
      theme: 'light',
      model_key: 'qwen2-1.5b',
      use_reranker: true,
      reranker_top_k: 3,
      initial_retrieval_k: 10,
    })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">⚙️ 设置</h2>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleReset}>
            重置
          </Button>
          <Button type="primary" icon={<SaveOutlined />} onClick={() => form.submit()}>
            保存设置
          </Button>
        </Space>
      </div>

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          theme: settings.theme,
          model_key: settings.model_config.model_key,
          use_reranker: settings.model_config.use_reranker,
          reranker_top_k: settings.model_config.reranker_top_k,
          initial_retrieval_k: settings.model_config.initial_retrieval_k,
        }}
        onFinish={handleSave}
      >
        <Card title="系统状态" className="!rounded-xl !border-gray-200 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <Tag color={systemStatus.api_connected ? 'success' : 'error'}>
                {systemStatus.api_connected ? '已连接' : '未连接'}
              </Tag>
              <span className="text-sm text-gray-600">技能树 API</span>
            </div>
            <div className="flex items-center gap-2">
              <Tag color={systemStatus.rag_connected ? 'success' : 'error'}>
                {systemStatus.rag_connected ? '已连接' : '未连接'}
              </Tag>
              <span className="text-sm text-gray-600">RAG API</span>
            </div>
            <div className="flex items-center gap-2">
              <Tag color={systemStatus.knowledge_base_ready ? 'success' : 'error'}>
                {systemStatus.knowledge_base_ready ? '就绪' : '未就绪'}
              </Tag>
              <span className="text-sm text-gray-600">知识库</span>
            </div>
            <div className="flex items-center gap-2">
              <Tag color={systemStatus.model_loaded ? 'success' : 'processing'}>
                {systemStatus.model_loaded ? '已加载' : '未加载'}
              </Tag>
              <span className="text-sm text-gray-600">
                {systemStatus.loaded_model || 'AI 模型'}
              </span>
            </div>
          </div>
        </Card>

        <Card title="外观设置" className="!rounded-xl !border-gray-200 mb-6">
          <Form.Item name="theme" label="主题模式">
            <Select
              options={[
                { value: 'light', label: '浅色模式' },
                { value: 'dark', label: '深色模式' },
                { value: 'auto', label: '跟随系统' },
              ]}
              style={{ width: 200 }}
            />
          </Form.Item>
        </Card>

        <Card title="模型配置" className="!rounded-xl !border-gray-200 mb-6">
          <Alert
            message="模型配置提示"
            description="模型首次加载可能需要几分钟时间，请耐心等待。推荐使用 Qwen2-1.5B 模型，在性能和效果之间取得良好平衡。"
            type="info"
            showIcon
            className="!mb-4 !rounded-lg"
          />

          <Form.Item name="model_key" label="选择模型">
            <Select
              style={{ width: 300 }}
              options={[
                {
                  value: 'qwen2-1.5b',
                  label: 'Qwen2-1.5B（推荐，约4GB显存）',
                },
                {
                  value: 'qwen2-0.5b',
                  label: 'Qwen2-0.5B（最快，适合CPU）',
                },
                {
                  value: 'chatglm3-6b',
                  label: 'ChatGLM3-6B（大模型，效果更好）',
                },
              ]}
            />
          </Form.Item>

          <Form.Item name="model_dir" label="模型下载路径">
            <Input.TextArea
              value={settings.model_config.model_dir}
              disabled
              autoSize={{ minRows: 1, maxRows: 2 }}
              className="!rounded-lg"
            />
          </Form.Item>

          <Divider />

          <Form.Item
            name="use_reranker"
            label="启用重排序功能"
            valuePropName="checked"
            extra="启用后，系统会先检索更多候选文档，再用重排序模型精排，提升答案质量"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="initial_retrieval_k"
            label="初始检索数量"
            extra="先检索这么多候选文档，再让重排序模型精排"
          >
            <Slider
              min={3}
              max={20}
              marks={{
                3: '3',
                10: '10',
                20: '20',
              }}
              style={{ width: 300 }}
            />
          </Form.Item>

          <Form.Item
            name="reranker_top_k"
            label="精排后保留数量"
            extra="重排序后保留最相关的几个文档喂给大模型"
          >
            <Slider
              min={1}
              max={5}
              marks={{
                1: '1',
                3: '3',
                5: '5',
              }}
              style={{ width: 300 }}
            />
          </Form.Item>

          <Alert
            message="流程说明"
            description="检索 10 个 → 重排序 → 取前 3 个 → 生成答案"
            type="success"
            showIcon
            className="!rounded-lg"
          />
        </Card>

        <Card title="API 配置" className="!rounded-xl !border-gray-200">
          <Form.Item label="技能树 API 地址">
            <Input.TextArea
              value={settings.api_base_url}
              disabled
              autoSize={{ minRows: 1, maxRows: 2 }}
              className="!rounded-lg"
            />
          </Form.Item>

          <Form.Item label="RAG API 地址">
            <Input.TextArea
              value={settings.rag_api_base_url}
              disabled
              autoSize={{ minRows: 1, maxRows: 2 }}
              className="!rounded-lg"
            />
          </Form.Item>
        </Card>
      </Form>
    </div>
  )
}
