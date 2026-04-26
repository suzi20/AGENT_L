import tiktoken
import json
from collections import Counter
import re

# ============ 初始化编码器 ============

encoding = tiktoken.get_encoding("cl100k_base")

print("\n" + "="*80)
print("🔬 深度 Token 分词解析")
print("="*80)

# ============ 第一部分：BPE 分词原理可视化 ============

print("\n【第一部分】BPE (Byte Pair Encoding) 原理演示")
print("-" * 80)

def visualize_tokenization(text: str, title: str = ""):
    """可视化分词过程"""
    print(f"\n📝 {title}")
    print(f"原文: '{text}'")
    
    # 编码
    tokens = encoding.encode(text)
    
    # 逐个 Token 解码
    token_details = []
    for i, token in enumerate(tokens):
        token_bytes = encoding.decode_single_token_bytes(token)
        token_str = token_bytes.decode('utf-8', errors='replace')
        token_details.append({
            'index': i,
            'id': token,
            'text': token_str,
            'bytes': token_bytes.hex(),
            'length': len(token_bytes)
        })
    
    print(f"Token数量: {len(tokens)}")
    print(f"\nToken 分解:")
    
    for detail in token_details:
        # 用颜色和格式展示 Token
        print(f"  [{detail['index']:2d}] ID:{detail['id']:6d} | " +
              f"Text: '{detail['text']:20s}' | " +
              f"Bytes: {detail['length']} | " +
              f"Hex: {detail['bytes']}")
    
    return token_details

# 示例 1: 英文单词如何分词
visualize_tokenization("hello", "英文单词: hello")
visualize_tokenization("engineering", "英文单词: engineering")

# 示例 2: 中文汉字如何分词
visualize_tokenization("你", "单个中文字: 你")
visualize_tokenization("你好", "两个中文字: 你好")
visualize_tokenization("你好世界", "四个中文字: 你好世界")

# 示例 3: 空格和标点的影响
visualize_tokenization("hello world", "带空格: hello world")
visualize_tokenization("hello-world", "带连字符: hello-world")
visualize_tokenization("hello, world!", "带标点: hello, world!")

# ============ 第二部分：字符级别分析 ============

print("\n" + "="*80)
print("【第二部分】字符级别分析")
print("-" * 80)

def char_level_analysis(text: str, title: str = ""):
    """字符级别的详细分析"""
    print(f"\n📊 {title}")
    
    tokens = encoding.encode(text)
    
    print(f"原文: '{text}'")
    print(f"字符数: {len(text)}")
    print(f"字节数: {len(text.encode('utf-8'))}")
    print(f"Token数: {len(tokens)}")
    
    # 按字符分析
    print(f"\n字符拆解:")
    for i, char in enumerate(text):
        char_bytes = char.encode('utf-8')
        print(f"  [{i:2d}] '{char}' → " +
              f"UTF-8: {char_bytes.hex()} " +
              f"({len(char_bytes)} 字节) " +
              f"Unicode: U+{ord(char):04X}")
    
    # 按 Token 分析
    print(f"\nToken 拆解:")
    token_to_chars = []
    for token_id in tokens:
        token_bytes = encoding.decode_single_token_bytes(token_id)
        token_str = token_bytes.decode('utf-8', errors='replace')
        token_to_chars.append({
            'id': token_id,
            'text': token_str,
            'bytes': token_bytes.hex(),
            'byte_count': len(token_bytes)
        })
        print(f"  ID:{token_id:6d} | Text:'{token_str:10s}' | " +
              f"Hex:{token_bytes.hex():20s} | Bytes:{len(token_bytes)}")
    
    return tokens, token_to_chars

# 测试用例
char_level_analysis("Hi", "英文: Hi (2字符)")
char_level_analysis("中", "中文: 中 (1字符)")
char_level_analysis("中文", "中文: 中文 (2字符)")

# ============ 第三部分：编码规律总结 ============

print("\n" + "="*80)
print("【第三部分】编码规律总结")
print("-" * 80)

patterns = {
    "ASCII字母": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "数字": "0123456789",
    "常见标点": ".,!?;:()[]{}",
    "数学符号": "+-*/<>=",
    "货币符号": "$€¥£",
    "中文汉字": "你好世界Python编程机器学习",
    "日文平假名": "あいうえお",
    "日文片假名": "アイウエオ",
    "中文标点": "，。；：？！",
}

print("\n各类字符的 Token 编码效率:\n")

for pattern_name, pattern_text in patterns.items():
    tokens = encoding.encode(pattern_text)
    ratio = len(tokens) / len(pattern_text)
    
    print(f"  {pattern_name:15s}: " +
          f"字符数={len(pattern_text):3d}, " +
          f"Token数={len(tokens):3d}, " +
          f"比率={ratio:.3f} Token/字符")

# ============ 第四部分：复杂文本分析 ============

print("\n" + "="*80)
print("【第四部分】复杂文本的分词策略")
print("-" * 80)

complex_texts = [
    "The quick brown fox",
    "The_quick_brown_fox",
    "TheQuickBrownFox",
    "the-quick-brown-fox",
    "THEQUICKBROWNFOX",
    "thequickbrownfox",
    "ThE qUiCk BrOwN FoX",
]

print("\n英文大小写和分隔符的影响:\n")

for text in complex_texts:
    tokens = encoding.encode(text)
    print(f"  '{text:30s}' → {len(tokens):2d} tokens")

# ============ 第五部分：中文字符频率分析 ============

print("\n" + "="*80)
print("【第五部分】中文编码的字节模式")
print("-" * 80)

chinese_text = "你好世界Python编程机器学习深度学习神经网络"
tokens = encoding.encode(chinese_text)

print(f"\n原文: {chinese_text}")
print(f"字符数: {len(chinese_text)}")
print(f"Token数: {len(tokens)}")
print(f"平均 Token/字符: {len(tokens)/len(chinese_text):.3f}")

print(f"\n详细分解:")

char_idx = 0
for i, token_id in enumerate(tokens):
    token_bytes = encoding.decode_single_token_bytes(token_id)
    token_str = token_bytes.decode('utf-8', errors='replace')
    
    # 分析这个 Token 对应的字节
    print(f"\n  Token[{i}] (ID:{token_id}):")
    print(f"    Text: '{token_str}'")
    print(f"    Bytes ({len(token_bytes)}字节): {token_bytes.hex()}")
    print(f"    Binary: {' '.join(format(b, '08b') for b in token_bytes)}")
    
    # 如果是中文，分析 UTF-8 编码
    if ord(token_str[0]) > 0x4E00:  # CJK 汉字范围
        print(f"    字符Unicode: U+{ord(token_str[0]):04X}")

# ============ 第六部分：Token 词表特性 ============

print("\n" + "="*80)
print("【第六部分】Token 词表特性分析")
print("-" * 80)

print(f"\nToken 词表大小: {encoding.n_vocab} 个")

# 分析一些特殊的 Token
special_tokens = {
    "空格": " ",
    "换行": "\n",
    "制表符": "\t",
    "英文缩写": "don't",
    "数字": "123",
    "emoji": "😀",
}

print(f"\n特殊 Token 分析:\n")

for desc, text in special_tokens.items():
    try:
        tokens = encoding.encode(text)
        token_details = []
        
        for token_id in tokens:
            token_bytes = encoding.decode_single_token_bytes(token_id)
            token_str = token_bytes.decode('utf-8', errors='replace')
            token_details.append(f"'{token_str}'(ID:{token_id})")
        
        print(f"  {desc:15s}: '{text}' → {' + '.join(token_details)}")
    except Exception as e:
        print(f"  {desc:15s}: 错误 - {e}")

# ============ 第七部分：实战对比 ============

print("\n" + "="*80)
print("【第七部分】实战文本对比")
print("-" * 80)

comparison_texts = [
    {
        "name": "官方文档片段（英文）",
        "text": "The model can understand and generate text in multiple languages. It performs exceptionally well on coding tasks."
    },
    {
        "name": "官方文档片段（中文）",
        "text": "该模型可以理解和生成多种语言的文本。它在编码任务上的表现特别出色。"
    },
    {
        "name": "代码片段（英文）",
        "text": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
    },
    {
        "name": "代码片段（中文注释）",
        "text": "def 斐波那契(n):\n    # 计算斐波那契数列\n    if n <= 1:\n        return n\n    return 斐波那契(n-1) + 斐波那契(n-2)"
    },
]

print()

results = []
for item in comparison_texts:
    name = item["name"]
    text = item["text"]
    
    tokens = encoding.encode(text)
    char_count = len(text)
    token_count = len(tokens)
    ratio = token_count / char_count if char_count > 0 else 0
    
    results.append({
        'name': name,
        'char_count': char_count,
        'token_count': token_count,
        'ratio': ratio
    })
    
    print(f"📄 {name}")
    print(f"   字符数: {char_count:4d} | Token数: {token_count:4d} | 比率: {ratio:.3f}")
    print()

# ============ 第八部分：优化建议 ============

print("="*80)
print("【第八部分】Token 优化实战建议")
print("-" * 80)

print("""
1️⃣  【英文优化】
   ✓ 使用缩写词: "don't" (2 tokens) vs "do not" (2 tokens) - 差不多
   ✓ 使用驼峰式: "camelCase" vs "camel_case" vs "camel case" - 驼峰最省
   ✓ 避免重复: "aaaaaa" vs "a a a a a a" - 前者更省
   
   示例对比:
""")

optimization_examples = [
    ("Please do not forget", "Please don't forget"),
    ("hello world example", "helloWorldExample"),
    ("a a a a a", "aaaaa"),
    ("Cannot be", "Can't be"),
]

for original, optimized in optimization_examples:
    orig_tokens = len(encoding.encode(original))
    opt_tokens = len(encoding.encode(optimized))
    saved = orig_tokens - opt_tokens
    
    symbol = "✓" if saved >= 0 else "✗"
    print(f"   {symbol} '{original}' ({orig_tokens}t) → '{optimized}' ({opt_tokens}t) | " +
          f"{'省' if saved > 0 else '增'} {abs(saved)}t")

print("""

2️⃣  【中文优化】
   ✗ 避免繁体字（通常更费Token）
   ✗ 避免多余的标点符号
   ✓ 使用更短的同义词
   ✓ 合并短句为长句（减少标点）
   
3️⃣  【混合语言优化】
   ✓ System prompt 用英文（更省）
   ✓ 用户内容保持中文（无法避免）
   ✓ 关键词用英文代码表示（如 API 名称）
   
4️⃣  【结构化数据】
   ✓ JSON 格式通常比自然语言省 Token
   ✓ 用数字编码代替文字
   ✓ 使用表格而不是长文本描述
""")

# ============ 总结 ============

print("\n" + "="*80)
print("📋 总结")
print("="*80)

print(f"""
Token 编码的本质:
  • BPE (Byte Pair Encoding) - 贪心地合并字节对
  • 英文单词在词表中，所以编码高效
  • 中文汉字多（>10000），不可能全部在词表中，需要多个Token
  
成本差异:
  • 英文: 每字符 0.25-0.3 Token
  • 中文: 每字符 0.8-1.2 Token
  • 中文成本是英文的 3-4 倍

优化策略:
  1. 尽量用英文写 System Prompt（节省基础Token）
  2. 预处理文本，移除不必要的内容
  3. 使用结构化格式而不是冗长文本
  4. 对重复内容做缓存
  5. 定期审计 API 费用，识别高成本文本
""")

print("="*80)
