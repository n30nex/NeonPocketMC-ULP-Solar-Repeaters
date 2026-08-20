#!/usr/bin/env python3
"""Package one PlatformIO ULP build with stable public filenames."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--family", choices=("esp", "nrf"), required=True)
    parser.add_argument("--version", default="v1.0.0-rc.1")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()

    source = Path(".pio/build") / args.env
    output = Path(args.output) / args.slug
    output.mkdir(parents=True, exist_ok=True)
    prefix = f"NeonPocketMC-ULP-{args.slug}-{args.version}"

    if args.family == "esp":
        inputs = (
            (source / "firmware.bin", output / f"{prefix}-app.bin"),
            (source / "firmware-merged.bin", output / f"{prefix}-full-recovery.bin"),
        )
    else:
        inputs = (
            (source / "firmware.uf2", output / f"{prefix}.uf2"),
            (source / "firmware.hex", output / f"{prefix}.hex"),
        )

    for src, dst in inputs:
        if not src.is_file():
            raise SystemExit(f"missing expected build output: {src}")
        shutil.copyfile(src, dst)

    manifest = output / "SHA256SUMS.txt"
    lines = [f"{sha256(path)}  {path.name}" for path in sorted(output.iterdir()) if path.is_file()]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Packaged {args.env} -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
