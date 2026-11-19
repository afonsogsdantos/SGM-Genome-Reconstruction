#!/usr/bin/env python3

import shutil
import subprocess
import tempfile
from pathlib import Path

READ1 = Path("data/cleaned/illumina_1.clean.fastq.gz")
READ2 = Path("data/cleaned/illumina_2.clean.fastq.gz")

OUTPUT = Path("results/assemblies/illumina/successful")

THREADS = 4
MEMORY_GB = 8

RESULT_FILES = [
    "contigs.fasta",
    "scaffolds.fasta",
    "spades.log",
    "params.txt",
]


def check_inputs():
    for path in (READ1, READ2):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Missing input file: {path}")


def main():
    check_inputs()

    # Use a temporary Linux directory without spaces.
    with tempfile.TemporaryDirectory(
        prefix="sgm_spades_",
        dir="/tmp"
    ) as temp_dir:

        work = Path(temp_dir)
        reads_dir = work / "reads"
        assembly_dir = work / "assembly"

        reads_dir.mkdir()

        temp_r1 = reads_dir / "illumina_1.fastq.gz"
        temp_r2 = reads_dir / "illumina_2.fastq.gz"

        print("[STEP 1/3] Copying cleaned reads", flush=True)

        shutil.copy2(READ1, temp_r1)
        shutil.copy2(READ2, temp_r2)

        command = [
            "spades.py",
            "--isolate",
            "-1", str(temp_r1),
            "-2", str(temp_r2),
            "-t", str(THREADS),
            "-m", str(MEMORY_GB),
            "-o", str(assembly_dir),
        ]

        print("\n[STEP 2/3] Running SPAdes", flush=True)
        print("[RUN]", " ".join(command), flush=True)

        subprocess.run(command, check=True)

        for filename in RESULT_FILES:
            result = assembly_dir / filename
            if not result.is_file() or result.stat().st_size == 0:
                raise RuntimeError(
                    f"Missing SPAdes result: {result}"
                )

        print("\n[STEP 3/3] Saving assembly", flush=True)

        OUTPUT.mkdir(parents=True, exist_ok=True)

        for filename in RESULT_FILES:
            source = assembly_dir / filename
            destination = OUTPUT / filename

            shutil.copy2(source, destination)
            print(f"[OK] Saved: {destination}", flush=True)

    print("\n[OK] Illumina assembly completed", flush=True)


if __name__ == "__main__":
    main()
