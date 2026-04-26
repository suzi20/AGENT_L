import tiktoken
from typing import List, Dict

print("\n" + "="*80)
print("🔄 Tiktoken 编码方式对比分析")
print("="*80)

# ============ 第一部分：可用的编码方式 ============

print("\n【第一部分】Tiktoken 支持的所有编码方式\n")

# 获取所有可用编码
encoding_names = [
    "o200k_base",      # GPT-4o 使用
    "cl100k_base",     # GPT-3.5-turbo, GPT-4 使用
    "p50k_base",       # Davinci-002, Davinci-003 使用
    "r50k_base",       # 旧模型 (gpt-3, gpt-2)
]

print("主要编码方式:")
for name in encoding_names:
    try:
        enc = tiktoken.get_encoding(name)
        vocab_size = enc.n_vocab
        print(f"  • {name:15s} - 词表大小: {vocab_size:6d} 个")
    except Exception as e:
        print(f"  • {name:15s} - 错误: {e}")

# ============ 第二部分：编码方式详解 ============

print("\n" + "="*80)
print("【第二部分】编码方式详细对比")
print("="*80)

encoding_info = {
    "o200k_base": {
        "model": "GPT-4o (最新)",
        "vocab_size": "200K tokens",
        "release": "2024年",
        "features": [
            "✓ 最新最优的编码方式",
            "✓ 对多语言（包括中文）优化更好",
            "✓ Token效率最高",
            "✓ 支持更多特殊字符",
        ]
    },
    "cl100k_base": {
        "model": "GPT-3.5-turbo, GPT-4",
        "vocab_size": "100K tokens",
        "release": "2023年",
        "features": [
            "✓ 应用最广泛",
            "✓ 相对稳定成熟",
            "✗ 中文效率不如o200k",
            "✗ 词表小于o200k",
        ]
    },
    "p50k_base": {
        "model": "Davinci-002/003",
        "vocab_size": "50K tokens",
        "release": "2022年",
        "features": [
            "✗ 较老的编码方式",
            "✗ 词表较小",
            "✗ 中文编码效率差",
            "✓ 仅用于特定旧模型",
        ]
    },
    "r50k_base": {
        "model": "GPT-3, GPT-2",
        "vocab_size": "50K tokens",
        "release": "2020年",
        "features": [
            "✗ 已过时",
            "✗ 不推荐使用",
            "✓ 只用于兼容旧代码",
        ]
    }
}

for enc_name, info in encoding_info.items():
    print(f"\n📌 {enc_name}")
    print(f"   模型: {info['model']}")
    print(f"   词表: {info['vocab_size']}")
    print(f"   发布: {info['release']}")
    print(f"   特点:")
    for feature in info['features']:
        print(f"      {feature}")

# ============ 第三部分：实际对比测试 ============

print("\n" + "="*80)
print("【第三部分】实际编码效率对比")
print("="*80)

test_texts = [
    {
        "name": "英文短句",
        "text": "Hello world, this is a test."
    },
    {
        "name": "中文短句",
        "text": "你好世界，这是一个测试。"
    },
    {
        "name": "中英混合",
        "text": "Hello 世界，This is 测试。"
    },
    {
        "name": "代码片段",
        "text": "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
    },
    {
        "name": "URL和符号",
        "text": "https://www.example.com/api?key=value&id=12345#section"
    },
    {
        "name": "JSON",
        "text": '{"name": "张三", "age": 25, "city": "北京"}'
    },
    {
        "name": "数学公式",
        "text": "E=mc², ∑(i=1 to n) = n(n+1)/2"
    },
]

# 创建对比表
print("\n比较各编码方式的 Token 数量:\n")

results = {}

for enc_name in encoding_names:
    try:
        encoding = tiktoken.get_encoding(enc_name)
        results[enc_name] = []
        
        print(f"\n{enc_name}:")
        print("-" * 80)
        
        for test in test_texts:
            text = test["text"]
            name = test["name"]
            
            tokens = encoding.encode(text)
            token_count = len(tokens)
            char_count = len(text)
            ratio = token_count / char_count if char_count > 0 else 0
            
            results[enc_name].append({
                'name': name,
                'token_count': token_count,
                'char_count': char_count,
                'ratio': ratio
            })
            
            print(f"  {name:15s}: 字符={char_count:3d}, Token={token_count:3d}, " +
                  f"比率={ratio:.3f}")
    
    except Exception as e:
        print(f"\n{enc_name}: 错误 - {e}")

# ============ 第四部分：编码效率对比总结 ============

print("\n" + "="*80)
print("【第四部分】编码效率排名")
print("="*80)

if results:
    # 选择一个测试用例做详细对比（中文短句）
    test_case_idx = 1  # 中文短句
    
    print(f"\n以 '{test_texts[test_case_idx]['name']}' 为例:\n")
    
    encodings_with_tokens = []
    for enc_name in encoding_names:
        if enc_name in results and len(results[enc_name]) > test_case_idx:
            token_count = results[enc_name][test_case_idx]['token_count']
            encodings_with_tokens.append((enc_name, token_count))
    
    # 排序
    encodings_with_tokens.sort(key=lambda x: x[1])
    
    for rank, (enc_name, token_count) in enumerate(encodings_with_tokens, 1):
        efficiency = "⭐" * (5 - rank) if rank <= 3 else ""
        symbol = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"  {symbol} 第{rank}名: {enc_name:15s} - {token_count:3d} tokens {efficiency}")

# ============ 第五部分：字节级别对比 ============

print("\n" + "="*80)
print("【第五部分】字节级别对比 - 中文字 '你' 的编码")
print("="*80)

char = "你"
print(f"\n字符: '{char}'")
print(f"Unicode: U+{ord(char):04X}")
print(f"UTF-8字节: {char.encode('utf-8').hex()}\n")

for enc_name in encoding_names:
    try:
        encoding = tiktoken.get_encoding(enc_name)
        tokens = encoding.encode(char)
        
        print(f"{enc_name}:")
        print(f"  Token 数: {len(tokens)}")
        
        for i, token_id in enumerate(tokens):
            token_bytes = encoding.decode_single_token_bytes(token_id)
            token_str = token_bytes.decode('utf-8', errors='replace')
            print(f"    [{i}] ID:{token_id:6d} | Hex:{token_bytes.hex():10s} | Text:'{token_str}'")
        print()
    
    except Exception as e:
        print(f"  错误: {e}\n")

# ============ 第六部分：性能和成本对比 ============

print("="*80)
print("【第六部分】性能和成本对比")
print("="*80)

print("""
📊 性能指标对比:

┌─────────────┬──────────┬──────────┬──────────┬──────────┐
│ 编码方式    │ 词表大小 │ 英文效率 │ 中文效率 │ 推荐度   │
├─────────────┼──────────┼──────────┼──────────┼──────────┤
│ o200k_base  │ 200K ⭐⭐⭐⭐⭐│ 高 ⭐⭐⭐⭐⭐│ 高 ⭐⭐⭐⭐│ 🌟🌟🌟🌟🌟│
│ cl100k_base │ 100K ⭐⭐⭐⭐ │ 高 ⭐⭐⭐⭐ │ 中 ⭐⭐⭐ │ 🌟🌟🌟🌟 │
│ p50k_base   │ 50K  ⭐⭐⭐    │ 中 ⭐⭐⭐   │ 低 ⭐⭐   │ 🌟🌟     │
│ r50k_base   │ 50K  ⭐⭐⭐    │ 中 ⭐⭐    │ 低 ⭐    │ 🌟      │
└─────────────┴──────────┴──────────┴──────────┴──────────┘

💰 成本估算 (基于100字符中文文本):

假设API费率: $0.002 per 1K tokens

  o200k_base:  ~300 tokens × $0.002/1K = $0.0006
  cl100k_base: ~350 tokens × $0.002/1K = $0.0007
  p50k_base:   ~380 tokens × $0.002/1K = $0.00076
  r50k_base:   ~400 tokens × $0.002/1K = $0.0008

节省成本: o200k vs cl100k 可省 ~15%
""")

# ============ 第七部分：选择建议 ============

print("="*80)
print("【第七部分】选择编码方式的建议")
print("="*80)

print("""
🎯 选择指南:

1. 新项目 - 使用 o200k_base ✅
   • GPT-4o 模型已成为主流
   • 编码效率最优
   • 对中文、特殊字符支持最好
   • 是未来的发展方向

2. 已有项目 - 继续使用 cl100k_base ✅
   • GPT-3.5/4 仍然广泛应用
   • 足够稳定成熟
   • 迁移成本不高，效果差异不大

3. 旧项目维护 - 使用 p50k_base ⚠️
   • 仅用于兼容旧模型 (Davinci-002/003)
   • 不建议新项目使用

4. 兼容性考虑 - 两种都支持 ✅
   • 大多数代码可以轻松在两者之间切换
   • 只需改一行: tiktoken.get_encoding("o200k_base")

📝 代码迁移示例:

# 旧代码
encoding = tiktoken.get_encoding("cl100k_base")

# 新代码
encoding = tiktoken.get_encoding("o200k_base")
""")

# ============ 第八部分：实际应用对比 ============

print("\n" + "="*80)
print("【第八部分】实际应用场景对比")
print("="*80)

scenarios = [
    {
        "name": "聊天机器人",
        "content": "你好！我想了解一下Python中的装饰器概念。Can you help me understand decorators in Python?",
        "tokens_estimation": {
            "o200k": "~45 tokens",
            "cl100k": "~52 tokens",
            "savings": "~13%"
        }
    },
    {
        "name": "文本总结",
        "content": """深度学习是机器学习的一个分支。
Deep learning is a subset of machine learning.
它使用人工神经网络来模拟人脑的学习过程。
It uses artificial neural networks to simulate brain learning.""",
        "tokens_estimation": {
            "o200k": "~35 tokens",
            "cl100k": "~40 tokens",
            "savings": "~12%"
        }
    },
    {
        "name": "代码生成",
        "content": "请生成一个Python函数来计算斐波那契数列。Generate a Python function to calculate Fibonacci sequence.",
        "tokens_estimation": {
            "o200k": "~25 tokens",
            "cl100k": "~28 tokens",
            "savings": "~11%"
        }
    },
]

print()
for scenario in scenarios:
    print(f"📱 {scenario['name']}")
    print(f"   示例: {scenario['content'][:50]}...")
    print(f"   o200k_base: {scenario['tokens_estimation']['o200k']}")
    print(f"   cl100k_base: {scenario['tokens_estimation']['cl100k']}")
    print(f"   节省: {scenario['tokens_estimation']['savings']}")
    print()

# ============ 第九部分：编码方式的内部差异 ============

print("="*80)
print("【第九部分】编码方式的内部算法差异")
print("="*80)

print("""
🔧 BPE (Byte Pair Encoding) 算法细节:

1. o200k_base (GPT-4o):
   • 基于 UTF-8 字节流
   • 最多进行 200K 次 merge 操作
   • 新增了许多中文和特殊字符的合并
   • 特殊处理多字节字符
   
   工作流程:
   "你" (UTF-8) → [0xE4, 0xBD, 0xA0] → 可能在1-2个Token内编码

2. cl100k_base (GPT-3.5/4):
   • 基于 UTF-8 字节流
   • 最多进行 100K 次 merge 操作
   • 中文字符合并不够充分
   • 通常需要3-4个Token来编码一个中文字
   
   工作流程:
   "你" (UTF-8) → [0xE4, 0xBD, 0xA0] → 通常需要3个Token

3. p50k_base / r50k_base (旧模型):
   • 基于 UTF-8 字节流
   • 仅进行 50K 次 merge 操作
   • 最小化的字符合并
   • 对中文的支持很差
   
   工作流程:
   "你" (UTF-8) → [0xE4, 0xBD, 0xA0] → 需要3个单独的字节Token

💡 总结:
   更多的 merge 操作 → 更好的字符组合 → 更少的 Token 需求
   特别是对于中文等多字节字符，编码方式的差异很大。
""")

# ============ 第十部分：总结表 ============

print("="*80)
print("【总结表】一句话总结")
print("="*80)

print("""
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 编码方式    ┃ 一句话总结                                   ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ o200k_base │ 最新最优，200K词表，中文友好，选它没错       │
│ cl100k_base│ 主流应用，100K词表，稳定成熟，广泛使用       │
│ p50k_base  │ 旧模型，50K词表，中文差，仅用兼容           │
│ r50k_base  │ 过时，50K词表，不推荐，除非维护旧代码       │
└─────────────┴────────────────────────────────────────────┘
""")

print("="*80)
print("✨ 编码方式对比分析完成！")
print("="*80)
