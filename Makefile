.DEFAULT_GOAL := all
.PHONY: all download download_reads download_reference verify_downloads

PYTHON := python3

# Pipeline inicial: obtencao e verificacao dos dados
all: download

download: download_reads download_reference
	@$(MAKE) verify_downloads

download_reads:
	$(PYTHON) scripts/download_ena.py

download_reference:
	$(PYTHON) scripts/download_reference.py

verify_downloads:
	@test -s data/raw/illumina_1.fastq.gz
	@test -s data/raw/illumina_2.fastq.gz
	@test -s data/raw/nanopore.fastq.gz
	@test -s data/reference/reference.fasta
	@echo "[OK] All input files are present and non-empty"

# Illumina quality control
.PHONY: qc_illumina

qc_illumina: results/qc/illumina/.complete

results/qc/illumina/.complete: scripts/quality_control.py environment.yml | download
	$(PYTHON) scripts/quality_control.py
	@test -s data/cleaned/illumina_1.clean.fastq.gz
	@test -s data/cleaned/illumina_2.clean.fastq.gz
	@test -s results/qc/illumina/fastp/fastp.json
	@test -s results/qc/illumina/raw/illumina_1_fastqc.zip
	@test -s results/qc/illumina/raw/illumina_2_fastqc.zip
	@test -s results/qc/illumina/clean/illumina_1.clean_fastqc.zip
	@test -s results/qc/illumina/clean/illumina_2.clean_fastqc.zip
	@touch $@
	@echo "[OK] Illumina quality control completed and verified"
