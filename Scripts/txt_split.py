from pathlib import Path

def split_to_about_500kb(src: Path, out_dir: Path,
                         target_kb: int = 500, slack_kb: int = 12,
                         encoding: str = "utf-8"):
    """
    将单个文本文件按“约500KB”切分到 out_dir。
    target_kb: 目标大小（KB）
    slack_kb: 允许的上浮空间（KB），用于更贴近目标而不频繁换新文件。
              实际硬上限 = target_kb + slack_kb
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    base = src.stem

    target_bytes = target_kb * 1024
    hard_max_bytes = (target_kb + slack_kb) * 1024  # 例如 500KB 目标 + 12KB 余量 = 512KB 上限

    part = 1
    current_bytes = 0
    w = None

    def open_new():
        nonlocal part, current_bytes, w
        if w:
            w.close()
        dst = out_dir / f"{base}_p{part:03d}.txt"
        w = dst.open("wb")  # 直接按字节写，避免重复编码
        part += 1
        current_bytes = 0

    with src.open("r", encoding=encoding, errors="ignore") as f:
        for line in f:
            b = line.encode(encoding)

            # 如果当前还没打开文件，或者再写这一行就会超过“硬上限”，就开新文件
            if w is None or (current_bytes > 0 and current_bytes + len(b) > hard_max_bytes):
                open_new()

            # 若这一行太长（大于硬上限），为了尽量保持可读性，这里作为单独一份写入；
            # 极少数情况下这份会略高于硬上限（通常不会发生，除非单行>512KB）
            if len(b) > hard_max_bytes and current_bytes == 0:
                w.write(b)
                open_new()
                continue

            # 正常写入
            w.write(b)
            current_bytes += len(b)

    if w:
        w.close()


if __name__ == "__main__":
    # 改成你的路径
    input_dir = Path(r"E:\Corpora\COCA\COCA_Aca\ori")
    output_dir = Path(r"E:\Corpora\COCA\COCA_Aca\split")  # 所有分片放在同一个大文件夹

    # 批量处理所有 .txt
    for src in sorted(input_dir.glob("*.txt")):
        print(f"处理: {src.name}")
        split_to_about_500kb(src, output_dir)

    print("完成！")
