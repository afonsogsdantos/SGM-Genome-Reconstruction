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
