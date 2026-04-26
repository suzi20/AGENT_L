#!/usr/bin/env python3
"""
快速启动脚本 - 本地 Ollama 聊天客户端
直接运行此脚本即可开始使用
"""

from chat import ChatClient
import sys

def main():
    print("\n" + "="*70)
    print("🤖 Ollama 聊天客户端 - 快速启动")
    print("="*70)
    print("""
📌 使用方式：

1. ✅ 确保 Ollama 已安装并运行
   • 下载: https://ollama.ai
   • 启动: ollama serve

2. ✅ 下载至少一个模型
   • ollama pull mistral     (推荐 - 快速)
   • ollama pull neural-chat (推荐 - 质量好)
   • ollama pull llama2      (稳定)

3. ✅ 运行此脚本
   • python quick_start.py

""")
    
    input("按 Enter 键继续...")
    
    print("\n🔍 初始化客户端...\n")
    
    try:
        # 创建客户端（使用 Ollama）
        client = ChatClient(
            use_ollama=True,
            model="mistral"  # 默认模型，可根据已安装的模型修改
        )
        
        # 进入交互模式
        client.interactive_mode()
        
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 检查清单：")
        print("   1. Ollama 是否已启动？(ollama serve)")
        print("   2. 是否已下载模型？(ollama pull mistral)")
        print("   3. 端口 11434 是否被占用？")
        sys.exit(1)

if __name__ == "__main__":
    main()
