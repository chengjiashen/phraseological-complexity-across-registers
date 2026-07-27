import os
import re
from collections import defaultdict

# ===== 提取年份（last_modified="YYYY" 或 unknown）=====
YEAR_RE = re.compile(r'last_modified="([^"]+)"')

def extract_year_from_s_line(line: str):
    m = YEAR_RE.search(line)
    if not m:
        return None  # 没年份 -> 当 unknown 处理
    val = m.group(1).strip()
    if val.lower() == "unknown":
        return None
    year = val[:4]
    return year if year.isdigit() else None


def parse_token_line(line: str):
    parts = line.strip().split("\t")
    if len(parts) == 9:
        return {
            "lemma": parts[2],
            "tag_simple": parts[4],
            "index": int(parts[6]),
            "head_index": int(parts[7]),
            "relation": parts[8],
        }
    return None


def extract_three_types(tokens):
    """
    return 3 dicts for one sentence:
      amod: adj+n
      dobj: v+n
      advV: adv+v
    """
    amod = defaultdict(int)
    dobj = defaultdict(int)
    advV = defaultdict(int)

    if not tokens:
        return amod, dobj, advV

    by_idx = {t["index"]: t for t in tokens}

    for tok in tokens:
        rel = tok["relation"]
        head_idx = tok["head_index"]
        if head_idx == 0 or head_idx not in by_idx:
            continue

        head = by_idx[head_idx]

        # amod: A -> N  => adj noun
        if rel == "amod" and tok["tag_simple"] == "A" and head["tag_simple"] == "N":
            key = f'{tok["lemma"]} {head["lemma"]}'
            amod[key] += 1

        # dobj: N -> V  => verb noun
        elif rel == "dobj" and tok["tag_simple"] == "N" and head["tag_simple"] == "V":
            key = f'{head["lemma"]} {tok["lemma"]}'
            dobj[key] += 1

        # advmod: R -> V => adverb verb
        elif rel == "advmod" and tok["tag_simple"] == "R" and head["tag_simple"] == "V":
            key = f'{tok["lemma"]} {head["lemma"]}'
            advV[key] += 1

    return amod, dobj, advV


def merge_counts(target, add):
    for k, v in add.items():
        target[k] += v


for n in range(1, 16):
    # ================= 主流程（单文件测试） =================

    filepath = f"D:/ENCOW16AX/txt/{n}/encow16ax{n}.txt"

    # year_stats[year]["amod"/"dobj"/"advV"][key] = freq
    year_stats = defaultdict(lambda: {
        "amod": defaultdict(int),
        "dobj": defaultdict(int),
        "advV": defaultdict(int),
    })

    current_year = None  # None = unknown/不统计
    current_sent_tokens = []

    with open(filepath, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # 句子开始：记录年份（unknown -> None）
            if line.startswith("<s "):
                current_year = extract_year_from_s_line(line)
                continue

            # 句子结束：处理（只有 current_year 有值才统计）
            if line.startswith("</s>"):
                if current_year is not None:
                    amod, dobj, advV = extract_three_types(current_sent_tokens)
                    merge_counts(year_stats[current_year]["amod"], amod)
                    merge_counts(year_stats[current_year]["dobj"], dobj)
                    merge_counts(year_stats[current_year]["advV"], advV)

                current_sent_tokens = []
                current_year = None
                continue

            # 跳过其他 XML 标签
            if line.startswith("<"):
                continue

            tok = parse_token_line(line)
            if tok is not None:
                current_sent_tokens.append(tok)

    # 文件末尾保险（同样只在有年份时统计）
    if current_sent_tokens and current_year is not None:
        amod, dobj, advV = extract_three_types(current_sent_tokens)
        merge_counts(year_stats[current_year]["amod"], amod)
        merge_counts(year_stats[current_year]["dobj"], dobj)
        merge_counts(year_stats[current_year]["advV"], advV)

    # ================= 输出：每个年份一个文件（完全汇总） =================

    out_dir = f"D:/ENCOW16AX/reference/{n}"
    os.makedirs(out_dir, exist_ok=True)

    for year in sorted(year_stats.keys()):

        combined = defaultdict(int)

        # 合并三类
        for d in ["amod", "dobj", "advV"]:
            for k, v in year_stats[year][d].items():
                combined[k] += v

        out_path = os.path.join(out_dir, f"{year}.txt")

        with open(out_path, "w", encoding="utf-8") as w:
            for k, v in sorted(combined.items(), key=lambda x: x[1], reverse=True):
                w.write(f"{k}\t{v}\n")

    print(f"Done. Pure merged yearly files written. Number {n}")