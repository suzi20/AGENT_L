# 🤖 我的第一个命令行聊天助手

一个功能完整的命令行聊天助手，支持多轮对话、历史管理、动态配置和本地/云端切换。

## 🚀 快速开始

### 安装依赖
```bash
# 只需要 Python 标准库，无需额外安装
python my_first_chatbot.py
```

### 基本使用

```
👤 你: 你好
🤖 你好！有什么我可以帮助你的吗？

👤 你: 用中文解释什么是递归
🤖 递归是指一个函数调用自身来解决问题...

👤 你: /history
📜 对话历史（最近 10 条）
1. 👤 你: 你好
2. 🤖 助手: 你好！有什么我可以帮助你的吗？
...

👤 你: /exit
👋 再见！
```

## 📋 完整命令列表

### 对话管理

```bash
/history [n]      # 查看最近 n 条对话（默认10条）
/clear            # 清空所有对话历史

示例:
  /history        # 查看最近10条
  /history 5      # 查看最近5条
  /clear          # 清空全部
```

### 参数配置

```bash
/temp [value]     # 设置温度（0.0-1.0）或查看当前值
/model [name]     # 切换模型或查看当前模型
/url [base]       # 切换基础 URL 或查看当前 URL
/config           # 显示完整配置

示例:
  /temp           # 查看当前温度
  /temp 0.3       # 设置为确定模式（创意低）
  /temp 0.9       # 设置为随意模式（创意高）
  
  /model          # 查看当前模型
  /model mistral  # 切换到 mistral 模型
  
  /url            # 查看当前 URL
  /url http://localhost:11434/api  # 切换到本地 Ollama
  
  /config         # 查看所有配置
```

### 文件操作

```bash
/save [file]      # 保存对话为 JSON 文件
/load [file]      # 加载之前保存的对话

示例:
  /save                    # 自动生成文件名保存
  /save my_chat.json       # 保存为指定文件名
  /load my_chat.json       # 加载对话
```

### 其他

```bash
/help             # 显示帮助信息
/exit 或 /quit    # 退出程序
```

## 🎯 常见使用场景

### 场景 1: 默认云端 API 对话

```bash
python my_first_chatbot.py

👤 你: Python 中什么是装饰器？
🤖 [获取云端 API 回复]

👤 你: /save today_chat.json
✅ 对话已保存到: today_chat.json

👤 你: /exit
```

### 场景 2: 切换到本地 Ollama

```bash
python my_first_chatbot.py

👤 你: /url http://localhost:11434/api
✅ URL 已切换为: http://localhost:11434/api
   来源: 🏠 本地 Ollama

👤 你: /model mistral
✅ 模型已切换为: mistral

👤 你: 你好
🤖 [本地模型回复]
```

### 场景 3: 调整创意水平

```bash
👤 你: 用低创意写一首诗
🤖 [低创意的诗歌]

👤 你: /temp 0.3
✅ 温度已更改为: 0.3

👤 你: 用创意写一首诗
🤖 [同样的提示，但更加确定和保守]

👤 你: /temp 0.9
✅ 温度已更改为: 0.9

👤 你: 用创意写一首诗
🤖 [高创意、更随意的诗歌]
```

### 场景 4: 对话持久化

```bash
# 第一次使用
python my_first_chatbot.py

👤 你: 什么是 AI？
👤 你: 它有什么应用？
👤 你: /save ai_discussion.json
✅ 对话已保存到: ai_discussion.json
👤 你: /exit

---

# 第二天继续对话
python my_first_chatbot.py

👤 你: /load ai_discussion.json
✅ 对话已加载: ai_discussion.json
   共 4 条消息
检测到保存的配置:
  基础 URL: https://dashscope.aliyuncs.com/compatible-mode/v1
  模型: qwen-turbo
  温度: 0.7
是否恢复这些配置？(y/n): y

👤 你: /history
👤 你: AI 的未来发展方向是什么？
```

## ⚙️ 配置选项

### 代码中修改默认配置

编辑 `my_first_chatbot.py` 最后的 `main()` 函数：

```python
def main():
    # 使用云端 API（默认）
    assistant = ChatAssistant(
        api_key="your-api-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-turbo"
    )
    
    # 或使用本地 Ollama
    # assistant = ChatAssistant(
    #     base_url="http://localhost:11434/api",
    #     model="mistral"
    # )
    
    assistant.run()
```

### 在运行时动态修改

```bash
👤 你: /config
⚙️  当前配置
基础 URL: https://dashscope.aliyuncs.com/compatible-mode/v1
模型: qwen-turbo
温度: 0.7
最大 Token: 2048
超时时间: 120s
对话条数: 3
最大历史: 50

👤 你: /url http://localhost:11434/api
👤 你: /model neural-chat
👤 你: /temp 0.5
👤 你: /config
```

## 📊 JSON 保存格式

对话会以以下格式保存：

```json
{
  "timestamp": "2026-04-26T10:30:45.123456",
  "config": {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo",
    "temperature": 0.7
  },
  "history": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好！有什么我可以帮助你的吗？"
    },
    ...
  ]
}
```

## 🔧 故障排除

### 问题：连接失败

```
❌ 错误: [Errno -2] Name or service not known
```

**解决方案：**
- 检查 API Key 是否正确：`/config` 查看 URL
- 检查网络连接
- 如果使用本地 Ollama，确保已启动：`ollama serve`

### 问题：模型不存在

```
❌ API 错误: Model not found
```

**解决方案：**
- 使用 `/model` 查看可用模型
- 确保模型已下载（Ollama）：`ollama list`

### 问题：请求超时

```
❌ 请求超时 (120s)
```

**解决方案：**
- 使用更小/更快的模型
- 检查网络连接
- 增加超时时间（修改代码中的 `request_timeout`）

## 💡 开发建议

### 添加新命令

在 `process_command` 方法中添加：

```python
elif command == '/new_cmd':
    self.cmd_new_feature(args)

def cmd_new_feature(self, args):
    """新功能说明"""
    print("✅ 新功能执行")
```

### 扩展功能

```python
# 1. 添加联网搜索
def cmd_search(self, query):
    # 实现搜索功能
    pass

# 2. 添加文件上传
def cmd_upload(self, filepath):
    # 实现文件上传
    pass

# 3. 添加多语言支持
self.language = "zh"  # 中文/英文切换
```

## 📝 完整工作流示例

```bash
$ python my_first_chatbot.py

🤖 我的第一个命令行聊天助手
======================================================================
📌 当前配置:
   基础URL: https://dashscope.aliyuncs.com/compatible-mode/v1
   模型: qwen-turbo
   温度: 0.7
   来源: ☁️  云端 API

💡 可用命令:
【对话管理】
  /history [n]  - 查看最近 n 条对话（默认10条）
  /clear        - 清空所有对话历史
...

🎯 开始对话（输入 /help 查看命令）
======================================================================

👤 你: 你好，介绍一下自己
🤖 你好！我是一个由阿里云百炼提供的 AI 助手...

👤 你: 用中文和我谈论 Python 中的装饰器
🤖 装饰器是 Python 中一个强大的功能...

👤 你: /history 5
📜 对话历史（最近 5 条）
1. 👤 你: 你好，介绍一下自己
2. 🤖 助手: 你好！我是一个由阿里云百炼提供的 AI 助手...
3. 👤 你: 用中文和我谈论 Python 中的装饰器
4. 🤖 助手: 装饰器是 Python 中一个强大的功能...
======================================================================

👤 你: /temp 0.3
✅ 温度已更改为: 0.3

👤 你: /save my_conversation.json
✅ 对话已保存到: my_conversation.json

👤 你: /exit

👋 再见！
```

## 🎓 学习路径

1. **基础使用**：运行程序，进行简单对话
2. **命令学习**：尝试各个 `/` 命令
3. **配置管理**：使用 `/temp`、`/model`、`/url` 切换参数
4. **数据持久化**：使用 `/save` 和 `/load` 管理对话
5. **切换服务**：在本地 Ollama 和云端 API 之间切换
6. **代码阅读**：理解 ChatAssistant 类的实现
7. **功能扩展**：添加自己的命令和功能

---

**祝你使用愉快！🎉**
