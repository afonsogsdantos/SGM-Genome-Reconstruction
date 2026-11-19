#!/usr/bin/env python3

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CONTIGS = Path("results/assemblies/illumina/successful/contigs.fasta")
REFERENCE = Path("data/reference/reference.fasta")
OUTPUT = Path("results/quast/illumina")

THREADS = 4
MIN_CONTIG = 500

REQUIRED_REPORTS = [
    "report.txt",
    "report.tsv",
    "report.html",
    "quast.log",
]


def check_inputs():
    for path in (CONTIGS, REFERENCE):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(
                f"Missing or empty input file: {path}"
            )


def main():
    check_inputs()

    # Use the system temporary directory for portability.
    # Require a path without spaces because QUAST does not support them.
    temp_root = Path(tempfile.gettempdir()).resolve()

    if " " in str(temp_root):
        raise RuntimeError(
            f"Temporary directory contains spaces: {temp_root}"
        )

    with tempfile.TemporaryDirectory(
        prefix="sgm_quast_",
        dir=temp_root
    ) as temp_dir:

        work = Path(temp_dir)
        input_dir = work / "input"
        quast_output = work / "output"

        input_dir.mkdir()

        temp_contigs = input_dir / "contigs.fasta"
        temp_reference = input_dir / "reference.fasta"

        print("[STEP 1/3] Preparing input files", flush=True)

        shutil.copy2(CONTIGS, temp_contigs)
        shutil.copy2(REFERENCE, temp_reference)

        command = [
            "quast.py",
            str(temp_contigs),
            "-r", str(temp_reference),
            "-o", str(quast_output),
            "-t", str(THREADS),
            "--min-contig", str(MIN_CONTIG),
            "--no-icarus",
        ]

        print("\n[STEP 2/3] Running QUAST", flush=True)
        print("[RUN]", " ".join(command), flush=True)

        subprocess.run(command, check=True)

        for filename in REQUIRED_REPORTS:
            result = quast_output / filename

            if not result.is_file() or result.stat().st_size == 0:
                raise RuntimeError(
                    f"Missing QUAST result: {result}"
                )

        print("\n[STEP 3/3] Saving QUAST results", flush=True)

        # Copy files and subdirectories, including detailed reports.
        # Existing results remain untouched if QUAST itself fails.
        OUTPUT.mkdir(parents=True, exist_ok=True)

        for source in quast_output.iterdir():
            destination = OUTPUT / source.name

            if source.is_dir():
                shutil.copytree(
                    source,
                    destination,
                    dirs_exist_ok=True
                )
            else:
                shutil.copy2(source, destination)

            print(f"[OK] Saved: {destination}", flush=True)

    print("\n[OK] Illumina QUAST evaluation completed", flush=True)


if __name__ == "__main__":
    main()
