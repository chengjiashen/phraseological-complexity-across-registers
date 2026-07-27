for n in range(1, 15):
    def parse_token_line(line):
        parts = line.strip().split("\t")
        if len(parts) == 9:
            return {
                "token": parts[0],  # 列1
                "tag": parts[1],  # 列2
                "lemma": parts[2],  # 列3
                "tag_simple": parts[4],  # 列5
                "index": int(parts[6]),  # 列7 -> int
                "head_index": int(parts[7]),  # 列8 -> int
                "relation": parts[8],  # 列9
            }
        return None


    filepath = f"D:/ENCOW16AX/content/{n}.txt"

    lemma_dict = {}
    amod_dict = {}
    advmod_dict = {}
    dobj_dict = {}
    current_sent = []

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if len(line) == 0:
                continue
            token_dict = parse_token_line(line)
            if token_dict is None:
                continue

            lemma = line.split("\t")[2]
            if lemma not in lemma_dict.keys():
                lemma_dict[lemma] = 1
            else:
                lemma_dict[lemma] += 1

            # —— 遇到新句开头：先“分析上一句”然后清空 —— #
            if token_dict["index"] == 1 and len(current_sent) != 0:

                # 建立句内 index -> token 的快速索引（O(1) 找 head）
                by_idx = {t["index"]: t for t in current_sent}

                # 逐个 token 做 amod / dobj 统计
                for tok in current_sent:
                    rel = tok["relation"]
                    head_idx = tok["head_index"]

                    # 跳过 root 或 head 缺失的情况
                    if head_idx == 0 or head_idx not in by_idx:
                        continue

                    head = by_idx[head_idx]

                    # amod: 形容词修饰名词（可按需放宽/删除这些类型过滤）
                    if rel == "amod" and tok["tag_simple"] == "A" and head["tag_simple"] == "N":
                        key = f'{tok["lemma"]} {head["lemma"]}'  # "adj noun"
                        amod_dict[key] = amod_dict.get(key, 0) + 1

                    # dobj: 名词作宾语，依赖动词（可按需放宽/删除这些类型过滤）
                    elif rel == "dobj" and tok["tag_simple"] == "N" and head["tag_simple"] == "V":
                        key = f'{head["lemma"]} {tok["lemma"]}'  # "verb noun"
                        dobj_dict[key] = dobj_dict.get(key, 0) + 1

                    # advmod:
                    elif rel == "advmod" and tok["tag_simple"] == "R" and head["tag_simple"] == "A":
                        key = f"{tok["lemma"]} {head["lemma"]}"
                        advmod_dict[key] = advmod_dict.get(key, 0) + 1
                    elif rel == "advmod" and tok["tag_simple"] == "R" and head["tag_simple"] == "V":
                        key = f"{tok["lemma"]} {head["lemma"]}"
                        advmod_dict[key] = advmod_dict.get(key, 0) + 1
                    elif rel == "advmod" and tok["tag_simple"] == "R" and head["tag_simple"] == "R":
                        key = f"{tok["lemma"]} {head["lemma"]}"
                        advmod_dict[key] = advmod_dict.get(key, 0) + 1

                # 清空上一句，准备收集新句
                current_sent = []

            # 把当前 token 加入正在构建的句子
            current_sent.append(token_dict)

    with open(f"D:/ENCOW16AX/write/amod{n}.txt", "w", encoding="utf-8") as file:
        for key in amod_dict.keys():
            file.write(f"{key} {amod_dict[key]}\n")

    with open(f"D:/ENCOW16AX/write/advmod{n}.txt", "w", encoding="utf-8") as file:
        for key in advmod_dict.keys():
            file.write(f"{key} {advmod_dict[key]}\n")

    with open(f"D:/ENCOW16AX/write/dobj{n}.txt", "w", encoding="utf-8") as file:
        for key in dobj_dict.keys():
            file.write(f"{key} {dobj_dict[key]}\n")

    with open(f"D:/ENCOW16AX/write/lemma{n}.txt", "w", encoding="utf-8") as file:
        for key in lemma_dict.keys():
            file.write(f"{key} {lemma_dict[key]}\n")

    print(f"Series {n} is done.")
