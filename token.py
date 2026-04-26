import tiktoken
import json

# ============ 初始化编码器 ============

# 使用 GPT-3.5/4 的编码方式
encoding = tiktoken.get_encoding("cl100k_base")

print("\n" + "="*70)
print("🔍 中英文 Token 编码对比分析")
print("="*70)

# ============ 测试文本 ============

test_cases = [
    {
        "name": "纯英文（短句）",
        "text": "Hello world"
    },
    {
        "name": "纯中文（短句）",
        "text": "你好世界"
    },
    {
        "name": "纯英文（长句）",
        "text": "Machine learning is a powerful technology that enables computers to learn from data without being explicitly programmed."
    },
    {
        "name": "纯中文（长句）",
        "text": "机器学习是一种强大的技术，使计算机能够在没有明确编程的情况下从数据中学习。"
    },
    {
        "name": "中英混合",
        "text": "Python是一种解释型编程语言。You can use it for machine learning, web development, and data analysis. 它具有简洁的语法和强大的库生态。"
    },
    {
        "name": "数字和符号",
        "text": "2024年，AI技术的成本下降了50%。The price dropped from $100 to $50. 这是一个重要的里程碑！"
    },
]

# ============ 编码和分析 ============

results = []

for case in test_cases:
    text = case["text"]
    name = case["name"]
    
    # 编码文本
    tokens = encoding.encode(text)
    token_count = len(tokens)
    
    # 计算字符数
    char_count = len(text)
    
    # 平均每个字符的 Token 数
    avg_tokens_per_char = token_count / char_count if char_count > 0 else 0
    
    # 解码来看具体的 Token 分割
    decoded_tokens = [encoding.decode_single_token_bytes(token) for token in tokens]
    
    result = {
        "name": name,
        "text": text,
        "char_count": char_count,
        "token_count": token_count,
        "avg_tokens_per_char": avg_tokens_per_char,
        "tokens": tokens,
        "decoded_tokens": [t.decode('utf-8', errors='ignore') for t in decoded_tokens]
    }
    
    results.append(result)
    
    # 打印详细信息
    print(f"\n📝 {name}")
    print("-" * 70)
    print(f"原文: {text}")
    print(f"字符数: {char_count}")
    print(f"Token数: {token_count}")
    print(f"平均每字符Token数: {avg_tokens_per_char:.3f}")
    print(f"编码后的Token: {tokens[:20]}{'...' if len(tokens) > 20 else ''}")
    print(f"Token分解: {result['decoded_tokens'][:20]}")

# ============ 对比分析 ============

print("\n" + "="*70)
print("📊 对比分析总结")
print("="*70)

en_short = results[0]
zh_short = results[1]
en_long = results[2]
zh_long = results[3]
mixed = results[4]

print(f"\n【短句对比】")
print(f"英文: '{en_short['text']}'")
print(f"  字符数: {en_short['char_count']}, Token数: {en_short['token_count']}")
print(f"中文: '{zh_short['text']}'")
print(f"  字符数: {zh_short['char_count']}, Token数: {zh_short['token_count']}")
print(f"💡 中文 Token 多 {zh_short['token_count'] / en_short['token_count']:.1f}x 倍")

print(f"\n【长句对比】")
print(f"英文: '{en_long['text'][:50]}...'")
print(f"  字符数: {en_long['char_count']}, Token数: {en_long['token_count']}")
print(f"中文: '{zh_long['text'][:50]}...'")
print(f"  字符数: {zh_long['char_count']}, Token数: {zh_long['token_count']}")
print(f"💡 中文 Token 多 {zh_long['token_count'] / en_long['token_count']:.1f}x 倍")

print(f"\n【混合文本】")
print(f"总字符数: {mixed['char_count']}, 总Token数: {mixed['token_count']}")
print(f"平均每字符Token数: {mixed['avg_tokens_per_char']:.3f}")

# ============ 深度分析 ============

print("\n" + "="*70)
print("🔬 深度分析：为什么中文更费Token？")
print("="*70)

print("""
1️⃣  【字节编码差异】
   - 英文: 字母是单字节 ASCII (a-z 0-9)
     例如: "hello" = 5个字符 = 2-3个Token
   
   - 中文: UTF-8 编码下，每个汉字占 3 个字节
     例如: "你好" = 2个字符 = 6个字节 = 2-3个Token
     
   结论: 中文 3 个字节 vs 英文 1 个字节 → 中文字节量多 3 倍

2️⃣  【词汇表大小】
   - BPE (Byte Pair Encoding) 是 tiktoken 的分词算法
   - 英文: 26个字母可组合成丰富的词汇，Token 词表充分覆盖
   - 中文: Unicode 中文汉字有数千个，难以全部编入 Token 词表
   - 结果: 中文需要用多个 Token 组合表示一个汉字
   
   例如: "中" 可能需要 2-3 个 Token 来编码

3️⃣  【空格和分词】
   - 英文: 用空格分词，自然边界清晰
     "machine learning" = 2个词 = 2个Token
   
   - 中文: 没有空格，需要逐字符处理
     "机器学习" = 4个字符 = 通常需要 4-6 个Token

4️⃣  【效率对比】
""")

# 计算效率
print(f"   英文平均效率: {1/en_long['avg_tokens_per_char']:.1f} 字符/Token")
print(f"   中文平均效率: {1/zh_long['avg_tokens_per_char']:.1f} 字符/Token")
print(f"   中文需要花费 {zh_long['avg_tokens_per_char'] / en_long['avg_tokens_per_char']:.1f}x 更多Token来表达相同字符")

# ============ 实际成本计算 ============

print("\n" + "="*70)
print("💰 实际成本计算（基于 OpenAI API 定价）")
print("="*70)

# 假设价格
price_per_1k_tokens = 0.002  # $0.002 per 1k tokens (example)

print(f"\n假设费率: ${price_per_1k_tokens} 每 1000 tokens")

for case in [en_long, zh_long]:
    cost = (case['token_count'] / 1000) * price_per_1k_tokens
    print(f"\n{case['name'] if 'name' in case else '文本'}")
    print(f"  Token数: {case['token_count']}")
    print(f"  成本: ${cost:.6f}")

# 相同字符数，中文成本更高
char_count = 100
en_cost = (char_count / en_long['avg_tokens_per_char'] / 1000) * price_per_1k_tokens
zh_cost = (char_count / zh_long['avg_tokens_per_char'] / 1000) * price_per_1k_tokens

print(f"\n【等长对比】100个字符：")
print(f"  英文估计成本: ${en_cost:.6f}")
print(f"  中文估计成本: ${zh_cost:.6f}")
print(f"  💡 中文成本约为英文的 {zh_cost/en_cost:.1f}x")

# ============ 优化建议 ============

print("\n" + "="*70)
print("⚡ 优化建议")
print("="*70)

print("""
1. 使用更高效的模型：
   - GPT-4o 比 GPT-3.5 对中文的编码更高效
   - 较新的模型有更优化的中文 Token 词表

2. 文本预处理：
   - 移除不必要的标点符号
   - 压缩重复的词语
   - 使用简化的表达方式

3. 提示词优化：
   - 用英文写 system prompt（英文更省Token）
   - 用中文写用户内容（无法避免）
   - 关键信息用英文缩写

4. 批量处理：
   - 合并多个短文本为一个请求
   - 减少 API 调用次数

5. 缓存策略：
   - 对重复的中文内容进行缓存
   - 避免重复编码相同文本
""")

print("\n" + "="*70)