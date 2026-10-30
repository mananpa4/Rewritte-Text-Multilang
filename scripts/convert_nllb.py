"""Descarga y convierte NLLB-200 distilled 600M a CTranslate2 int8."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="facebook/nllb-200-distilled-600M")
    parser.add_argument("--out", default="models/nllb-200-distilled-600M-int8")
    args = parser.parse_args()
    output = Path(args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "ctranslate2.converters.transformers",
        "--model",
        args.model,
        "--output_dir",
        str(output),
        "--quantization",
        "int8",
        "--copy_files",
        "tokenizer.json",
        "tokenizer_config.json",
        "sentencepiece.bpe.model",
        "special_tokens_map.json",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
