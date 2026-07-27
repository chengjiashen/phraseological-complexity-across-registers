"""
Split large text files into smaller chunks while preserving line boundaries.

The script processes all matching text files in an input directory and writes
the resulting chunks to a specified output directory. Chunk sizes are measured
in kibibytes, where 1 KB equals 1,024 bytes.

Example
-------
python split_text_files.py \
    "D:/ENCOW16AX/content" \
    "D:/ENCOW16AX/split" \
    --target-kb 100000 \
    --slack-kb 12
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SplitResult:
    """Summary of a completed file-splitting operation."""

    source_file: Path
    output_files: tuple[Path, ...]
    total_bytes_written: int

    @property
    def number_of_chunks(self) -> int:
        """Return the number of output chunks created."""
        return len(self.output_files)


def split_text_file(
    source_file: Path,
    output_dir: Path,
    target_kb: int = 100000,
    slack_kb: int = 12,
    encoding: str = "utf-8",
    decoding_errors: str = "strict",
    overwrite: bool = False,
) -> SplitResult:
    """
    Split a text file into chunks without breaking individual lines.

    Each chunk is allowed to grow up to ``target_kb + slack_kb``. A new chunk
    is created when writing the next complete line would exceed that limit.

    Parameters
    ----------
    source_file
        Path to the source text file.
    output_dir
        Directory in which the output chunks will be stored.
    target_kb
        Target chunk size in kibibytes.
    slack_kb
        Additional size allowance in kibibytes.
    encoding
        Character encoding used to read and encode the source file.
    decoding_errors
        Strategy for handling decoding errors. Common values are ``"strict"``,
        ``"replace"``, and ``"ignore"``.
    overwrite
        Whether existing chunks generated from the same source file should be
        deleted before processing.

    Returns
    -------
    SplitResult
        Information about the generated output files.

    Raises
    ------
    FileNotFoundError
        If the source file does not exist.
    IsADirectoryError
        If the source path points to a directory.
    ValueError
        If the size parameters are invalid.
    FileExistsError
        If matching output chunks already exist and ``overwrite`` is false.
    """
    source_file = source_file.resolve()
    output_dir = output_dir.resolve()

    if not source_file.exists():
        raise FileNotFoundError(f"Source file does not exist: {source_file}")

    if not source_file.is_file():
        raise IsADirectoryError(f"Source path is not a file: {source_file}")

    if target_kb <= 0:
        raise ValueError("target_kb must be greater than zero.")

    if slack_kb < 0:
        raise ValueError("slack_kb must be zero or greater.")

    output_dir.mkdir(parents=True, exist_ok=True)

    output_pattern = f"{source_file.stem}_p*.txt"
    existing_output_files = sorted(output_dir.glob(output_pattern))

    if existing_output_files and not overwrite:
        raise FileExistsError(
            f"Output chunks already exist for {source_file.name}. "
            "Use --overwrite to replace them."
        )

    if overwrite:
        for existing_file in existing_output_files:
            existing_file.unlink()

    hard_limit_bytes = (target_kb + slack_kb) * 1024

    output_files: list[Path] = []
    output_file: BinaryIO | None = None
    current_chunk_size = 0
    total_bytes_written = 0
    chunk_number = 0

    def close_current_chunk() -> None:
        """Close the current output chunk, if one is open."""
        nonlocal output_file, current_chunk_size

        if output_file is not None:
            output_file.close()
            output_file = None
            current_chunk_size = 0

    def open_new_chunk() -> None:
        """Open the next numbered output chunk."""
        nonlocal output_file, current_chunk_size, chunk_number

        chunk_number += 1
        output_path = (
            output_dir
            / f"{source_file.stem}_p{chunk_number:03d}.txt"
        )

        output_file = output_path.open("wb")
        output_files.append(output_path)
        current_chunk_size = 0

    try:
        with source_file.open(
            mode="r",
            encoding=encoding,
            errors=decoding_errors,
            newline="",
        ) as input_file:
            for line_number, line in enumerate(input_file, start=1):
                encoded_line = line.encode(encoding)
                line_size = len(encoded_line)

                if output_file is None:
                    open_new_chunk()

                if (
                    current_chunk_size > 0
                    and current_chunk_size + line_size > hard_limit_bytes
                ):
                    close_current_chunk()
                    open_new_chunk()

                if line_size > hard_limit_bytes:
                    LOGGER.warning(
                        "%s, line %d is larger than the configured chunk "
                        "limit and will be written as an oversized chunk.",
                        source_file.name,
                        line_number,
                    )

                # output_file is guaranteed to be open at this point.
                assert output_file is not None

                output_file.write(encoded_line)
                current_chunk_size += line_size
                total_bytes_written += line_size

    finally:
        close_current_chunk()

    return SplitResult(
        source_file=source_file,
        output_files=tuple(output_files),
        total_bytes_written=total_bytes_written,
    )


def process_directory(
    input_dir: Path,
    output_dir: Path,
    file_pattern: str,
    target_kb: int,
    slack_kb: int,
    encoding: str,
    decoding_errors: str,
    overwrite: bool,
) -> int:
    """
    Split all matching text files in a directory.

    Returns
    -------
    int
        Exit status. Zero indicates success; one indicates that at least one
        file could not be processed.
    """
    input_dir = input_dir.resolve()

    if not input_dir.exists():
        LOGGER.error("Input directory does not exist: %s", input_dir)
        return 1

    if not input_dir.is_dir():
        LOGGER.error("Input path is not a directory: %s", input_dir)
        return 1

    source_files = sorted(
        path for path in input_dir.glob(file_pattern) if path.is_file()
    )

    if not source_files:
        LOGGER.warning(
            "No files matching %r were found in %s.",
            file_pattern,
            input_dir,
        )
        return 0

    successful_files = 0
    failed_files = 0
    total_chunks = 0

    for source_file in source_files:
        LOGGER.info("Processing %s", source_file.name)

        try:
            result = split_text_file(
                source_file=source_file,
                output_dir=output_dir,
                target_kb=target_kb,
                slack_kb=slack_kb,
                encoding=encoding,
                decoding_errors=decoding_errors,
                overwrite=overwrite,
            )
        except Exception:
            failed_files += 1
            LOGGER.exception("Failed to process %s", source_file.name)
            continue

        successful_files += 1
        total_chunks += result.number_of_chunks

        LOGGER.info(
            "Created %d chunk(s) from %s.",
            result.number_of_chunks,
            source_file.name,
        )

    LOGGER.info(
        "Processing complete: %d file(s) succeeded, %d file(s) failed, "
        "and %d chunk(s) were created.",
        successful_files,
        failed_files,
        total_chunks,
    )

    return 1 if failed_files else 0


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Split text files into smaller chunks while preserving complete "
            "lines."
        )
    )

    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing the source text files.",
    )

    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory in which the output chunks will be saved.",
    )

    parser.add_argument(
        "--pattern",
        default="*.txt",
        help='File pattern to process. Default: "*.txt".',
    )

    parser.add_argument(
        "--target-kb",
        type=int,
        default=100000,
        help="Target chunk size in KB. Default: 100000.",
    )

    parser.add_argument(
        "--slack-kb",
        type=int,
        default=12,
        help="Additional permitted chunk size in KB. Default: 12.",
    )

    parser.add_argument(
        "--encoding",
        default="utf-8",
        help='Text encoding of the source files. Default: "utf-8".',
    )

    parser.add_argument(
        "--decoding-errors",
        choices=("strict", "replace", "ignore"),
        default="strict",
        help=(
            "How decoding errors should be handled. "
            'Default: "strict".'
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing chunks generated from the same source files.",
    )

    return parser.parse_args()


def main() -> int:
    """Run the command-line program."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    arguments = parse_arguments()

    return process_directory(
        input_dir=arguments.input_dir,
        output_dir=arguments.output_dir,
        file_pattern=arguments.pattern,
        target_kb=arguments.target_kb,
        slack_kb=arguments.slack_kb,
        encoding=arguments.encoding,
        decoding_errors=arguments.decoding_errors,
        overwrite=arguments.overwrite,
    )


if __name__ == "__main__":
    raise SystemExit(main())
