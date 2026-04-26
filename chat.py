import json
import urllib.request
import urllib.error
import socket
from typing import List, Dict, Optional, Generator
from datetime import datetime
import sys
import time

class ChatClient:
    """手搓的聊天客户端 - 支持云端 API 和本地 Ollama"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None, use_ollama: bool = False):
        """
        初始化聊天客户端
        
        Args:
            api_key: API密钥（云端服务使用）
            base_url: API基础URL
            model: 模型名称
            use_ollama: 是否使用本地 Ollama（默认 False）
        """
        self.use_ollama = use_ollama
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 20
        self.request_timeout = 120
        
        if use_ollama:
            # 本地 Ollama 配置
            self.base_url = base_url or "http://localhost:11434/api"
            self.model = model or "llama2"  # 默认 llama2
            self.api_key = None
            print(f"✅ 使用本地 Ollama - 模型: {self.model}")
            self._check_ollama_available()
        else:
            # 云端 API 配置
            self.api_key = api_key
            self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            self.model = model or "qwen-turbo"
            print(f"✅ 使用云端 API - 模型: {self.model}")
    
    def _check_ollama_available(self):
        """检查本地 Ollama 是否可用"""
        try:
            req = urllib.request.Request(
                url=f"{self.base_url.replace('/api', '')}/api/tags",
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                models = [m['name'] for m in data.get('models', [])]
                print(f"✅ Ollama 连接成功！可用模型: {models}")
                
                # 检查请求的模型是否存在
                if models and self.model not in models:
                    print(f"⚠️  警告: 模型 '{self.model}' 未找到，可用模型: {models}")
                    self.model = models[0]  # 使用第一个可用模型
                    print(f"📝 已切换到模型: {self.model}")
        except Exception as e:
            print(f"❌ Ollama 连接失败: {e}")
            print(f"   💡 请确保 Ollama 已启动: ollama serve")
    
    def _build_request(self, messages: List[Dict], stream: bool = False) -> Dict:
        """构建API请求的JSON体"""
        if self.use_ollama:
            # Ollama 格式
            return {
                "model": self.model,
                "messages": messages,
                "stream": stream
            }
        else:
            # 云端 API 格式
            return {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                "temperature": 0.7,
                "max_tokens": 2048
            }
    
    def _send_request(self, payload: Dict) -> Optional[str]:
        """发送HTTP请求并获取响应（支持流式和 Ollama）"""
        try:
            # 将字典转换为JSON字符串
            data = json.dumps(payload).encode('utf-8')
            
            # 构建 URL
            if self.use_ollama:
                url = f"{self.base_url}/chat"
            else:
                url = f"{self.base_url}/chat/completions"
            
            # 构建请求头
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # 创建请求
            req = urllib.request.Request(
                url=url,
                data=data,
                headers=headers
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                response_text = response.read().decode('utf-8')
                return response_text
                
        except socket.timeout:
            print(f"❌ 请求超时({self.request_timeout}秒)")
            print(f"   💡 建议: 检查网络或切换更快的模型")
            return None
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP错误: {e.code}")
            error_msg = e.read().decode('utf-8')
            print(f"   错误信息: {error_msg}")
            return None
        except urllib.error.URLError as e:
            print(f"❌ 网络错误: {e.reason}")
            return None
        except Exception as e:
            print(f"❌ 请求错误: {str(e)}")
            return None
    
    def _parse_response(self, response_text: str) -> Optional[str]:
        """解析API响应"""
        try:
            response_json = json.loads(response_text)
            
            # 检查是否有错误
            if 'error' in response_json:
                print(f"❌ API错误: {response_json['error'].get('message', '未知错误')}")
                return None
            
            # 提取回复内容
            if 'choices' in response_json and len(response_json['choices']) > 0:
                choice = response_json['choices'][0]
                if 'message' in choice:
                    return choice['message'].get('content', '')
                elif 'delta' in choice:
                    return choice['delta'].get('content', '')
            
            return None
            
        except json.JSONDecodeError:
            print(f"❌ JSON解析错误")
            return None
        except Exception as e:
            print(f"❌ 响应解析错误: {str(e)}")
            return None
    
    def _stream_response(self, response_text: str) -> Generator[str, None, None]:
        """流式解析响应（支持 Ollama 和云端 API）"""
        for line in response_text.split('\n'):
            if not line.strip():
                continue
            
            # Ollama 格式：直接是 JSON 行
            if self.use_ollama:
                try:
                    chunk = json.loads(line)
                    if 'message' in chunk:
                        content = chunk['message'].get('content', '')
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue
            else:
                # 云端 API 格式：需要 'data: ' 前缀
                if line.startswith('data: '):
                    json_str = line[6:].strip()
                    
                    if json_str == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(json_str)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            
                            content = delta.get('content')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
    
    def chat(self, user_message: str, use_history: bool = True, stream: bool = True) -> str:
        """
        核心聊天函数
        
        Args:
            user_message: 用户输入的消息
            use_history: 是否使用对话历史
            stream: 是否使用流式响应
            
        Returns:
            模型的回复
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 保持历史记录长度
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # 构建消息列表
        if use_history:
            messages = self.conversation_history
        else:
            messages = [{"role": "user", "content": user_message}]
        
        # 构建请求
        payload = self._build_request(messages, stream=stream)
        
        # 发送请求
        print(f"🤖 正在思考...", end="", flush=True)
        response_text = self._send_request(payload)
        print("\r" + " " * 20 + "\r", end="", flush=True)  # 清除"正在思考"提示
        
        if response_text is None:
            return ""
        
        # 处理流式或非流式响应
        if stream:
            full_response = ""
            print("🤖 ", end="", flush=True)
            
            for chunk in self._stream_response(response_text):
                print(chunk, end="", flush=True)
                sys.stdout.flush()
                full_response += chunk
            
            print()  # 换行
        else:
            full_response = self._parse_response(response_text)
            if full_response:
                print(f"🤖 {full_response}")
        
        # 添加助手回复到历史
        if full_response:
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
        
        return full_response
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("📋 对话历史已清空")
    
    def show_history(self):
        """显示对话历史"""
        print("\n" + "="*60)
        print("📜 对话历史")
        print("="*60)
        
        if not self.conversation_history:
            print("(空)")
            return
        
        for i, msg in enumerate(self.conversation_history, 1):
            role = "👤 用户" if msg['role'] == 'user' else "🤖 助手"
            content = msg['content']
            # 截断长内容
            if len(content) > 80:
                content = content[:80] + "..."
            print(f"{i}. {role}: {content}")
        print("="*60 + "\n")
    
    def export_history(self, filename: str = "chat_history.json"):
        """导出对话历史为JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            print(f"✅ 对话历史已保存到 {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def interactive_mode(self):
        """交互模式 - 像 ChatGPT 一样连续对话"""
        print("\n" + "="*70)
        print("🤖 ChatGPT 式交互模式")
        print("="*70)
        print("💡 命令：")
        print("   输入消息 - 与 AI 对话")
        print("   /history - 查看对话历史")
        print("   /clear   - 清空对话历史")
        print("   /save    - 保存对话历史")
        print("   /help    - 显示帮助")
        print("   /exit    - 退出")
        print("="*70 + "\n")
        
        while True:
            try:
                # 获取用户输入
                user_input = input("👤 你: ").strip()
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.startswith('/'):
                    command = user_input.lower()
                    
                    if command == '/exit' or command == '/quit':
                        print("\n👋 再见！")
                        break
                    elif command == '/history':
                        self.show_history()
                    elif command == '/clear':
                        confirm = input("确定要清空对话历史吗？(y/n): ").strip().lower()
                        if confirm == 'y':
                            self.clear_history()
                    elif command == '/save':
                        self.export_history()
                    elif command == '/help':
                        print("""
可用命令:
  /history - 查看完整对话历史
  /clear   - 清空所有对话历史
  /save    - 将对话历史导出为 JSON 文件
  /exit    - 退出交互模式
  /help    - 显示此帮助信息
                        """)
                    else:
                        print(f"❓ 未知命令: {user_input}")
                
                else:
                    # 正常对话
                    self.chat(user_input, use_history=True, stream=True)
                    print()  # 空行分隔
            
            except KeyboardInterrupt:
                print("\n\n👋 被中断，已退出")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")


# ============ 使用示例 ============

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🤖 ChatClient - 支持云端 API 和本地 Ollama")
    print("="*70)
    print("\n选择使用方式：")
    print("  1. 本地 Ollama (推荐 - 免费、无需 API Key)")
    print("  2. 云端 API (需要 API Key)")
    print("  3. 退出")
    print()
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        # 使用本地 Ollama
        print("\n🔍 检查本地 Ollama...")
        client = ChatClient(
            use_ollama=True,
            model="llama2"  # 可改为: mistral, neural-chat, starling-lm 等
        )
        print("\n💡 提示: 如果 Ollama 未启动，请在新终端运行: ollama serve")
        client.interactive_mode()
    
    elif choice == "2":
        # 使用云端 API
        api_key = input("\n请输入 API Key: ").strip()
        if not api_key:
            print("❌ API Key 不能为空")
        else:
            client = ChatClient(
                api_key=api_key,
                model="qwen-turbo"
            )
            client.interactive_mode()
    
    else:
        print("👋 再见！")
