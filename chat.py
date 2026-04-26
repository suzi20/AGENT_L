import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Generator
from datetime import datetime
import sys

class ChatClient:
    """手搓的聊天客户端 - 不依赖任何框架"""
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        """
        初始化聊天客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = "deepseek-r1-distill-qwen-32b"
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10  # 最多保留10条对话历史
    
    def _build_request(self, messages: List[Dict], stream: bool = False) -> Dict:
        """构建API请求的JSON体"""
        return {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 2048
        }
    
    def _send_request(self, payload: Dict) -> Optional[str]:
        """发送HTTP请求并获取响应"""
        try:
            # 将字典转换为JSON字符串
            data = json.dumps(payload).encode('utf-8')
            
            # 创建请求
            req = urllib.request.Request(
                url=f"{self.base_url}/chat/completions",
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=60) as response:
                response_text = response.read().decode('utf-8')
                return response_text
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP错误: {e.code}")
            print(f"   错误信息: {e.read().decode('utf-8')}")
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
        """流式解析响应（处理Server-Sent Events格式）"""
        for line in response_text.split('\n'):
            if line.startswith('data: '):
                # 移除 'data: ' 前缀
                json_str = line[6:].strip()
                
                # 跳过[DONE]标记
                if json_str == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(json_str)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        
                        # 优先获取content，如果没有则获取reasoning_content
                        content = delta.get('content')
                        if content:
                            yield content
                        elif 'reasoning_content' in delta:
                            # 处理思考过程
                            yield f"[思考] {delta['reasoning_content']}"
                            
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
        print(f"🤖 正在思考...")
        response_text = self._send_request(payload)
        
        if response_text is None:
            return ""
        
        # 处理流式或非流式响应
        if stream:
            full_response = ""
            print("🤖 ", end="", flush=True)
            
            for chunk in self._stream_response(response_text):
                print(chunk, end="", flush=True)
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
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"{i}. {role}: {content}")
        print("="*60 + "\n")


# ============ 使用示例 ============

# 初始化客户端
client = ChatClient(
    api_key="sk-33365590761c4e349834395404a259f5"
)

# 测试1: 单轮对话
print("\n" + "="*60)
print("测试1: 单轮对话")
print("="*60)
response = client.chat("Python中什么是装饰器？")
print()

# 测试2: 多轮对话（有历史）
print("="*60)
print("测试2: 多轮对话（有历史）")
print("="*60)
response = client.chat("能给我一个实际的例子吗？")
print()

# 测试3: 查看对话历史
client.show_history()

# 测试4: 清空历史后重新开始
client.clear_history()
response = client.chat("你好，我是一个新用户")
print()