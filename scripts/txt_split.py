from pathlib import Path


def split_to_about_500kb(
    src: Path,
    out_dir: Path,
    target_kb: int = 100000,
    slack_kb: int = 12,
    encoding: str = "utf-8"
):
    """
    Split a single text file into chunks of approximately the target size
    and save them in ``out_dir``.

    Parameters
    ----------
    src : Path
        Path to the source text file.
    out_dir : Path
        Directory in which the split files will be saved.
    target_kb : int, default=100000
        Target size of each output file, in kilobytes.
    slack_kb : int, default=12
        Additional size allowance, in kilobytes. This makes it possible to
        keep files close to the target size without creating a new file too
        frequently. The actual maximum size is ``target_kb + slack_kb``.
    encoding : str, default="utf-8"
        Character encoding used to read and encode the source file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    base = src.stem

    target_bytes = target_kb * 1024
    hard_max_bytes = (target_kb + slack_kb) * 1024
    # For example, a 500 KB target plus a 12 KB allowance gives a 512 KB limit.

    part = 1
    current_bytes = 0
    w = None

    def open_new():
        """Close the current output file and open a new file chunk."""
        nonlocal part, current_bytes, w

        if w:
            w.close()

        dst = out_dir / f"{base}_p{part:03d}.txt"
        w = dst.open("wb")  # Write bytes directly to avoid repeated encoding.
        part += 1
        current_bytes = 0

    with src.open("r", encoding=encoding, errors="ignore") as f:
        for line in f:
            b = line.encode(encoding)

            # Open a new file if no output file is currently open or if writing
            # the next line would cause the current file to exceed the hard limit.
            if (
                w is None
                or (
                    current_bytes > 0
                    and current_bytes + len(b) > hard_max_bytes
                )
            ):
                open_new()

            # If a single line is larger than the hard limit, write it as a
            # separate chunk to preserve readability. In this rare case, the
            # output file may exceed the hard limit.
            if len(b) > hard_max_bytes and current_bytes == 0:
                w.write(b)
                open_new()
                continue

            # Write the line to the current output file.
            w.write(b)
            current_bytes += len(b)

    if w:
        w.close()


if __name__ == "__main__":
    # Replace these paths with the appropriate local directories.
    input_dir = Path(r"D:/ENCOW16AX/content")
    output_dir = Path(r"D:/ENCOW16AX/split")
    # All split files will be stored in the same output directory.

    # Process all .txt files in the input directory.
    for src in sorted(input_dir.glob("*.txt")):
        print(f"Processing: {src.name}")
        split_to_about_500kb(src, output_dir)

    print("Processing complete!")
