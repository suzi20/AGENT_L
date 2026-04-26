#!/usr/bin/env python3
"""
我的第一个命令行聊天助手
支持多轮对话、历史记录、动态配置、本地/云端切换
"""

import json
import urllib.request
import urllib.error
import socket
from typing import List, Dict, Optional, Generator
from datetime import datetime
import sys
import os

class ChatAssistant:
    """命令行聊天助手 - 功能完整版"""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model: str = "qwen-turbo"
    ):
        """
        初始化聊天助手
        
        Args:
            api_key: API密钥
            base_url: API基础URL（支持切换到本地 Ollama）
            model: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # 对话管理
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 50  # 最多保存50条消息
        
        # 参数配置
        self.temperature = 0.7  # 温度（0-1，越高越随意）
        self.max_tokens = 2048
        self.request_timeout = 120
        
        # 状态
        self.is_ollama = "localhost" in base_url or "127.0.0.1" in base_url
        
        print("\n" + "="*70)
        print("🤖 我的第一个命令行聊天助手")
        print("="*70)
        self._print_status()
        print()
    
    def _print_status(self):
        """打印当前状态"""
        print(f"📌 当前配置:")
        print(f"   基础URL: {self.base_url}")
        print(f"   模型: {self.model}")
        print(f"   温度: {self.temperature}")
        print(f"   来源: {'🏠 本地 Ollama' if self.is_ollama else '☁️  云端 API'}")
        if not self.is_ollama and self.api_key:
            print(f"   API Key: {self.api_key[:10]}...")
    
    def _build_request(self, messages: List[Dict], stream: bool = False) -> Dict:
        """构建API请求"""
        if self.is_ollama:
            # Ollama 格式
            return {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                "temperature": self.temperature
            }
        else:
            # 云端 API 格式
            return {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
    
    def _send_request(self, payload: Dict) -> Optional[str]:
        """发送请求并获取响应"""
        try:
            data = json.dumps(payload).encode('utf-8')
            
            # 构建 URL
            if self.is_ollama:
                url = f"{self.base_url}/chat"
            else:
                url = f"{self.base_url}/chat/completions"
            
            # 构建请求头
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            req = urllib.request.Request(url=url, data=data, headers=headers)
            
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                return response.read().decode('utf-8')
        
        except socket.timeout:
            print(f"❌ 请求超时 ({self.request_timeout}s)")
            return None
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP 错误: {e.code}")
            return None
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None
    
    def _parse_response(self, response_text: str) -> Optional[str]:
        """解析API响应"""
        try:
            response_json = json.loads(response_text)
            
            if 'error' in response_json:
                print(f"❌ API 错误: {response_json['error'].get('message', '未知错误')}")
                return None
            
            # 根据格式提取内容
            if 'choices' in response_json and response_json['choices']:
                choice = response_json['choices'][0]
                if 'message' in choice:
                    return choice['message'].get('content', '')
                elif 'delta' in choice:
                    return choice['delta'].get('content', '')
            
            return None
        except json.JSONDecodeError:
            print(f"❌ JSON 解析错误")
            return None
        except Exception as e:
            print(f"❌ 解析错误: {e}")
            return None
    
    def _stream_response(self, response_text: str) -> Generator[str, None, None]:
        """流式解析响应"""
        for line in response_text.split('\n'):
            if not line.strip():
                continue
            
            if self.is_ollama:
                # Ollama 格式
                try:
                    chunk = json.loads(line)
                    if 'message' in chunk:
                        content = chunk['message'].get('content', '')
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue
            else:
                # 云端 API 格式
                if line.startswith('data: '):
                    json_str = line[6:].strip()
                    if json_str == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(json_str)
                        if 'choices' in chunk and chunk['choices']:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
    
    def chat(self, user_message: str, stream: bool = True) -> str:
        """
        发送消息并获取回复
        
        Args:
            user_message: 用户消息
            stream: 是否流式输出
            
        Returns:
            AI 的回复
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 保持历史长度
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # 构建请求
        payload = self._build_request(self.conversation_history, stream=stream)
        
        # 发送请求
        print("🤖 ", end="", flush=True)
        response_text = self._send_request(payload)
        
        if response_text is None:
            return ""
        
        # 解析响应
        if stream:
            full_response = ""
            for chunk in self._stream_response(response_text):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()
        else:
            full_response = self._parse_response(response_text) or ""
            print(full_response)
        
        # 添加助手回复到历史
        if full_response:
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
        
        return full_response
    
    # ============ 命令处理 ============
    
    def cmd_clear(self):
        """清空对话历史"""
        self.conversation_history = []
        print("✅ 对话历史已清空")
    
    def cmd_history(self, limit: int = 10):
        """查看对话历史"""
        print("\n" + "="*70)
        print(f"📜 对话历史（最近 {min(limit, len(self.conversation_history))} 条）")
        print("="*70)
        
        if not self.conversation_history:
            print("(空)")
            return
        
        messages = self.conversation_history[-limit:]
        for i, msg in enumerate(messages, 1):
            role = "👤 你" if msg['role'] == 'user' else "🤖 助手"
            content = msg['content']
            if len(content) > 60:
                content = content[:60] + "..."
            print(f"{i}. {role}: {content}")
        print("="*70 + "\n")
    
    def cmd_temp(self, temp: Optional[float] = None):
        """获取/设置温度"""
        if temp is None:
            print(f"当前温度: {self.temperature}")
            print("💡 温度范围: 0.0 (确定) ~ 1.0 (随意)")
        else:
            if 0.0 <= temp <= 1.0:
                self.temperature = temp
                print(f"✅ 温度已更改为: {self.temperature}")
            else:
                print("❌ 温度必须在 0.0 ~ 1.0 之间")
    
    def cmd_model(self, model: Optional[str] = None):
        """获取/切换模型"""
        if model is None:
            print(f"当前模型: {self.model}")
        else:
            self.model = model
            print(f"✅ 模型已切换为: {self.model}")
    
    def cmd_base_url(self, url: Optional[str] = None):
        """获取/切换基础URL"""
        if url is None:
            print(f"当前 URL: {self.base_url}")
            print("💡 常用 URL:")
            print("   - 云端: https://dashscope.aliyuncs.com/compatible-mode/v1")
            print("   - 本地: http://localhost:11434/api")
        else:
            self.base_url = url
            self.is_ollama = "localhost" in url or "127.0.0.1" in url
            print(f"✅ URL 已切换为: {self.base_url}")
            print(f"   来源: {'🏠 本地 Ollama' if self.is_ollama else '☁️  云端 API'}")
    
    def cmd_config(self):
        """显示当前配置"""
        print("\n" + "="*70)
        print("⚙️  当前配置")
        print("="*70)
        print(f"基础 URL: {self.base_url}")
        print(f"模型: {self.model}")
        print(f"温度: {self.temperature}")
        print(f"最大 Token: {self.max_tokens}")
        print(f"超时时间: {self.request_timeout}s")
        print(f"对话条数: {len(self.conversation_history)}")
        print(f"最大历史: {self.max_history}")
        print("="*70 + "\n")
    
    def cmd_save(self, filename: Optional[str] = None):
        """保存对话历史为 JSON"""
        if filename is None:
            filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "base_url": self.base_url,
                    "model": self.model,
                    "temperature": self.temperature
                },
                "history": self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 对话已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def cmd_load(self, filename: str):
        """加载对话历史"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.conversation_history = data.get('history', [])
            
            # 选择是否恢复配置
            config = data.get('config', {})
            if config:
                print(f"检测到保存的配置:")
                print(f"  基础 URL: {config.get('base_url')}")
                print(f"  模型: {config.get('model')}")
                print(f"  温度: {config.get('temperature')}")
                
                restore = input("是否恢复这些配置？(y/n): ").strip().lower()
                if restore == 'y':
                    self.base_url = config.get('base_url', self.base_url)
                    self.model = config.get('model', self.model)
                    self.temperature = config.get('temperature', self.temperature)
                    self.is_ollama = "localhost" in self.base_url or "127.0.0.1" in self.base_url
            
            print(f"✅ 对话已加载: {filename}")
            print(f"   共 {len(self.conversation_history)} 条消息")
        except Exception as e:
            print(f"❌ 加载失败: {e}")
    
    def cmd_help(self):
        """显示帮助信息"""
        print("""
💡 可用命令:

【对话管理】
  /history [n]  - 查看最近 n 条对话（默认10条）
  /clear        - 清空所有对话历史

【参数配置】
  /temp [value] - 设置温度（0.0-1.0）或查看当前值
  /model [name] - 切换模型或查看当前模型
  /url [base]   - 切换基础 URL 或查看当前 URL
  /config       - 显示完整配置

【文件操作】
  /save [file]  - 保存对话为 JSON 文件
  /load [file]  - 加载之前保存的对话

【其他】
  /help         - 显示此帮助信息
  /exit         - 退出程序

【快速配置】
  切换到本地 Ollama:
    /url http://localhost:11434/api
    /model mistral
    
  切换到云端 API:
    /url https://dashscope.aliyuncs.com/compatible-mode/v1
    /model qwen-turbo
        """)
    
    def process_command(self, command: str, args: str):
        """处理命令"""
        if command == '/clear':
            self.cmd_clear()
        elif command == '/history':
            limit = int(args) if args and args.isdigit() else 10
            self.cmd_history(limit)
        elif command == '/temp':
            if args:
                try:
                    self.cmd_temp(float(args))
                except ValueError:
                    print(f"❌ 温度值必须是数字")
            else:
                self.cmd_temp()
        elif command == '/model':
            self.cmd_model(args if args else None)
        elif command == '/url':
            self.cmd_base_url(args if args else None)
        elif command == '/config':
            self.cmd_config()
        elif command == '/save':
            self.cmd_save(args if args else None)
        elif command == '/load':
            if not args:
                print("❌ 用法: /load <filename>")
            else:
                self.cmd_load(args)
        elif command == '/help':
            self.cmd_help()
        elif command == '/exit' or command == '/quit':
            return False
        else:
            print(f"❓ 未知命令: {command}")
        
        return True
    
    def run(self):
        """运行交互模式"""
        self.cmd_help()
        
        print("\n" + "="*70)
        print("🎯 开始对话（输入 /help 查看命令）")
        print("="*70 + "\n")
        
        while True:
            try:
                # 获取用户输入
                user_input = input("👤 你: ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input.startswith('/'):
                    parts = user_input.split(' ', 1)
                    command = parts[0]
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if not self.process_command(command, args):
                        print("\n👋 再见！\n")
                        break
                
                else:
                    # 正常对话
                    self.chat(user_input, stream=True)
                    print()
            
            except KeyboardInterrupt:
                print("\n\n👋 已退出\n")
                break
            except Exception as e:
                print(f"❌ 错误: {e}\n")


# ============ 主程序 ============

def main():
    """主函数"""
    
    # 创建助手
    # 这里可以修改 api_key 和 base_url 来配置
    assistant = ChatAssistant(
        api_key="sk-",  # 替换为你的 API Key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-turbo"
    )
    
    # 如果你想使用本地 Ollama，改为：
    # assistant = ChatAssistant(
    #     base_url="http://localhost:11434/api",
    #     model="mistral"
    # )
    
    # 运行
    assistant.run()


if __name__ == "__main__":
    main()
