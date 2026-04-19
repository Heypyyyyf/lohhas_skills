#!/usr/bin/env python3
"""
material-pool 状态管理脚本
用于：正样本/负样本库管理、相似度计算、事件日志
"""
import json
import os
import sys
from pathlib import Path

STATE_DIR = Path(__file__).parent.parent / "state"
STATE_DIR.mkdir(exist_ok=True)

LIKED_FILE = STATE_DIR / "liked_topics.json"
REJECTED_FILE = STATE_DIR / "rejected_topics.json"
EVENTS_FILE = STATE_DIR / "events.jsonl"


def load_json(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── n-gram 相似度 ──────────────────────────────────────

def char_ngrams(text, n=2):
    """字符 n-gram 集合"""
    return set(text.lower()[i:i+n] for i in range(len(text) - n + 1))


def word_tokens(text):
    """简单分词（中文按字符，英文按空格）"""
    import re
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return set(text.split())


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def seq_similarity(s1, s2):
    """序列相似度（最长公共子序列 / 较短长度）"""
    if not s1 or not s2:
        return 0.0
    m, n = len(s1), len(s2)
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return 2 * dp[m][n] / (m + n)


def similarity(a_text, b_text):
    """
    综合相似度：字符 2-gram Jaccard + 3-gram Jaccard + 词 Jaccard + 序列相似度
    取最大值
    """
    c2_a, c2_b = char_ngrams(a_text, 2), char_ngrams(b_text, 2)
    c3_a, c3_b = char_ngrams(a_text, 3), char_ngrams(b_text, 3)
    w_a, w_b = word_tokens(a_text), word_tokens(b_text)

    scores = [
        jaccard(c2_a, c2_b),
        jaccard(c3_a, c3_b),
        jaccard(w_a, w_b),
        seq_similarity(a_text.lower(), b_text.lower()),
    ]
    return max(scores)


# ── 命令行接口 ──────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "init":
        save_json(LIKED_FILE, [])
        save_json(REJECTED_FILE, [])
        print("[OK] 状态文件初始化完成")
        print(f"  liked:     {LIKED_FILE}")
        print(f"  rejected:  {REJECTED_FILE}")
        print(f"  events:    {EVENTS_FILE}")

    elif cmd == "like":
        payload = json.loads(sys.argv[2].replace("'", '"')) if len(sys.argv) > 2 else {}
        items = load_json(LIKED_FILE)
        items.append(payload)
        save_json(LIKED_FILE, items)
        print(f"[OK] 正样本已记录: {payload.get('title', '?')}")

    elif cmd == "reject":
        payload = json.loads(sys.argv[2].replace("'", '"')) if len(sys.argv) > 2 else {}
        items = load_json(REJECTED_FILE)
        # 生成唯一 ID
        import hashlib, time
        item_id = hashlib.md5(f"{payload.get('title','')}{time.time()}".encode()).hexdigest()[:8]
        payload["id"] = f"rej_{item_id}"
        payload["rejected_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        items.append(payload)
        save_json(REJECTED_FILE, items)
        print(f"[OK] 负样本已记录: {payload.get('title', '?')} (id={payload['id']})")

    elif cmd == "similarity":
        text = ""
        against = "rejected"
        topk = 3
        for i, arg in enumerate(sys.argv[2:], start=2):
            if arg == "--text" and len(sys.argv) > i+1:
                text = sys.argv[i+1]
            if arg == "--against" and len(sys.argv) > i+1:
                against = sys.argv[i+1]
            if arg == "--topk" and len(sys.argv) > i+1:
                topk = int(sys.argv[i+1])

        if not text:
            print("[ERROR] --text 参数必填")
            sys.exit(1)

        pool_file = REJECTED_FILE if against == "rejected" else LIKED_FILE
        pool = load_json(pool_file)
        scored = []
        for item in pool:
            score = similarity(text, item.get("title", ""))
            scored.append((score, item))
        scored.sort(reverse=True)
        top = scored[:topk]
        print(f"[RESULT] 相似度分析 (top {len(top)})")
        for score, item in top:
            print(f"  {score:.3f}  {item.get('id','?')}  {item.get('title','?')}")

    elif cmd == "event":
        import time
        payload = json.loads(sys.argv[2].replace("'", '"')) if len(sys.argv) > 2 else {}
        event = {
            "event": payload.pop("event", "unknown"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": payload
        }
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(f"[OK] 事件已记录: {event['event']}")

    elif cmd == "help":
        print("""用法:
  python3 material_pool_state.py init
  python3 material_pool_state.py like   '{"title":"...","score":8}'
  python3 material_pool_state.py reject '{"title":"...","reason":"low_value","stage":"filter"}'
  python3 material_pool_state.py similarity --text "话题标题" --against rejected --topk 3
  python3 material_pool_state.py event   '{"event":"filter.scored","accepted":3}'""")

    else:
        print(f"[ERROR] 未知命令: {cmd}")
        print("用 'help' 查看用法")
