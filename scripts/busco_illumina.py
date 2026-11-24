#!/usr/bin/env python3

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CONTIGS = Path("results/assemblies/illumina/successful/contigs.fasta")
OUTPUT = Path("results/busco/illumina")

LINEAGE = "staphylococcus_odb12.2"
THREADS = 4

SUMMARY_TXT = f"short_summary.specific.{LINEAGE}.illumina.txt"
SUMMARY_JSON = f"short_summary.specific.{LINEAGE}.illumina.json"


def check_inputs():
    if not CONTIGS.is_file() or CONTIGS.stat().st_size == 0:
        raise FileNotFoundError(f"Missing contigs: {CONTIGS}")


def main():
    check_inputs()

    temp_root = Path(tempfile.gettempdir()).resolve()

    # Keep downloaded BUSCO datasets between executions.
    cache_root = Path.home() / ".cache" / "sgm_busco"
    cache_root.mkdir(parents=True, exist_ok=True)

    if " " in str(temp_root) or " " in str(cache_root):
        raise RuntimeError(
            "BUSCO working and cache paths must not contain spaces"
        )

    with tempfile.TemporaryDirectory(
        prefix="sgm_busco_",
        dir=temp_root
    ) as temp_dir:

        work = Path(temp_dir)
        input_dir = work / "input"
        output_dir = work / "output"

        input_dir.mkdir()

        temp_contigs = input_dir / "contigs.fasta"

        print("[STEP 1/3] Preparing contigs", flush=True)
        shutil.copy2(CONTIGS, temp_contigs)

        command = [
            "busco",
            "-i", str(temp_contigs),
            "-m", "genome",
            "-l", LINEAGE,
            "-o", "illumina",
            "--out_path", str(output_dir),
            "--download_path", str(cache_root),
            "-c", str(THREADS),
        ]

        print("\n[STEP 2/3] Running BUSCO", flush=True)
        print("[RUN]", " ".join(command), flush=True)

        subprocess.run(command, check=True)

        run_output = output_dir / "illumina"

        for filename in (SUMMARY_TXT, SUMMARY_JSON):
            result = run_output / filename

            if not result.is_file() or result.stat().st_size == 0:
                raise RuntimeError(
                    f"Missing BUSCO report: {result}"
                )

        print("\n[STEP 3/3] Saving BUSCO results", flush=True)

        OUTPUT.mkdir(parents=True, exist_ok=True)

        for source in run_output.iterdir():
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

    print("\n[OK] Illumina BUSCO evaluation completed", flush=True)


if __name__ == "__main__":
    main()
