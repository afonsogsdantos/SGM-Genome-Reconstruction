#!/usr/bin/env python3

import subprocess
from pathlib import Path

RAW = Path("data/raw")
CLEAN = Path("data/cleaned")
QC = Path("results/qc/illumina")

RAW_R1 = RAW / "illumina_1.fastq.gz"
RAW_R2 = RAW / "illumina_2.fastq.gz"

CLEAN_R1 = CLEAN / "illumina_1.clean.fastq.gz"
CLEAN_R2 = CLEAN / "illumina_2.clean.fastq.gz"

RAW_QC = QC / "raw"
CLEAN_QC = QC / "clean"
FASTP_QC = QC / "fastp"


def run(command):
    print("\n[RUN]", " ".join(map(str, command)), flush=True)
    subprocess.run([str(item) for item in command], check=True)


def check_inputs():
    for path in (RAW_R1, RAW_R2):
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Missing input file: {path}")


def main():
    check_inputs()

    for folder in (CLEAN, RAW_QC, CLEAN_QC, FASTP_QC):
        folder.mkdir(parents=True, exist_ok=True)

    print("\n[STEP 1/3] Initial FastQC", flush=True)

    run([
        "fastqc",
        "--threads", "4",
        "--outdir", RAW_QC,
        RAW_R1,
        RAW_R2,
    ])

    print("\n[STEP 2/3] fastp filtering", flush=True)

    run([
        "fastp",
        "--in1", RAW_R1,
        "--in2", RAW_R2,
        "--out1", CLEAN_R1,
        "--out2", CLEAN_R2,
        "--detect_adapter_for_pe",
        "--cut_right",
        "--cut_right_window_size", "4",
        "--cut_right_mean_quality", "20",
        "--length_required", "50",
        "--thread", "4",
        "--html", FASTP_QC / "fastp.html",
        "--json", FASTP_QC / "fastp.json",
        "--report_title", "SGM Illumina quality filtering",
    ])

    print("\n[STEP 3/3] Final FastQC", flush=True)

    run([
        "fastqc",
        "--threads", "4",
        "--outdir", CLEAN_QC,
        CLEAN_R1,
        CLEAN_R2,
    ])

    print("\n[OK] Illumina quality control completed", flush=True)


if __name__ == "__main__":
    main()
