"""Simple, defensive antivirus-style scanner.

This script scans files for known malicious hashes or byte patterns.
It is intended for educational and defensive purposes only.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import os
from pathlib import Path
from typing import Iterable, Iterator, List, Sequence


@dataclasses.dataclass(frozen=True)
class Signature:
    name: str
    kind: str  # "sha256" or "bytes"
    value: bytes


DEFAULT_SIGNATURES: List[Signature] = [
    Signature(
        name="EICAR-Test-File",
        kind="bytes",
        value=(
            b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!"
        ),
    ),
]


def iter_paths(root: Path, extensions: Sequence[str]) -> Iterator[Path]:
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            path = Path(dirpath) / filename
            if extensions and path.suffix.lower() not in extensions:
                continue
            yield path


def sha256_digest(path: Path) -> bytes:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.digest()


def scan_bytes(path: Path, needle: bytes, max_bytes: int) -> bool:
    with path.open("rb") as handle:
        data = handle.read(max_bytes)
    return needle in data


def load_custom_signatures(lines: Iterable[str]) -> List[Signature]:
    signatures: List[Signature] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        kind, name, value = stripped.split(",", 2)
        if kind == "sha256":
            signatures.append(Signature(name=name, kind=kind, value=bytes.fromhex(value)))
        elif kind == "bytes":
            signatures.append(Signature(name=name, kind=kind, value=value.encode("utf-8")))
        else:
            raise ValueError(f"Unsupported signature kind: {kind}")
    return signatures


def scan_file(
    path: Path,
    signatures: Sequence[Signature],
    max_bytes: int,
) -> List[str]:
    matches: List[str] = []
    digest = sha256_digest(path)
    for signature in signatures:
        if signature.kind == "sha256" and digest == signature.value:
            matches.append(signature.name)
        elif signature.kind == "bytes" and scan_bytes(path, signature.value, max_bytes):
            matches.append(signature.name)
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Defensive antivirus-style scanner.")
    parser.add_argument("root", type=Path, help="Root directory to scan")
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[],
        help="Optional file extensions to scan (e.g. .exe .dll .py)",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=2 * 1024 * 1024,
        help="Maximum bytes to read for byte-pattern signatures",
    )
    parser.add_argument(
        "--signatures",
        type=Path,
        help="Optional CSV file of signatures: kind,name,value",
    )
    args = parser.parse_args()

    extensions = [ext.lower() for ext in args.extensions]
    signatures = list(DEFAULT_SIGNATURES)
    if args.signatures:
        signatures.extend(load_custom_signatures(args.signatures.read_text().splitlines()))

    hits: List[str] = []
    for path in iter_paths(args.root, extensions):
        try:
            matches = scan_file(path, signatures, args.max_bytes)
        except (OSError, ValueError) as exc:
            hits.append(f"ERROR: {path} ({exc})")
            continue
        for match in matches:
            hits.append(f"MATCH: {path} -> {match}")

    print("Scan complete.")
    if not hits:
        print("No matches found.")
        return 0

    print("Findings:")
    for hit in hits:
        print(f"- {hit}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
