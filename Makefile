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

# Illumina genome assembly
.PHONY: assemble_illumina

assemble_illumina: results/assemblies/illumina/.complete

results/assemblies/illumina/.complete: scripts/assemble_illumina.py environment.yml results/qc/illumina/.complete
	$(PYTHON) scripts/assemble_illumina.py
	@test -s results/assemblies/illumina/successful/contigs.fasta
	@test -s results/assemblies/illumina/successful/scaffolds.fasta
	@test -s results/assemblies/illumina/successful/spades.log
	@test -s results/assemblies/illumina/successful/params.txt
	@touch $@
	@echo "[OK] Illumina assembly completed and verified"

# Illumina assembly evaluation with QUAST
.PHONY: quast_illumina

quast_illumina: results/quast/illumina/.complete

results/quast/illumina/.complete: scripts/evaluate_illumina.py results/assemblies/illumina/.complete
	$(PYTHON) scripts/evaluate_illumina.py
	@test -s results/quast/illumina/report.txt
	@test -s results/quast/illumina/report.tsv
	@test -s results/quast/illumina/report.html
	@test -s results/quast/illumina/quast.log
	@touch $@
	@echo "[OK] Illumina QUAST evaluation completed and verified"

# Illumina assembly completeness with BUSCO
.PHONY: busco_illumina

busco_illumina: results/busco/illumina/.complete

results/busco/illumina/.complete: scripts/busco_illumina.py environment.yml results/assemblies/illumina/.complete
	$(PYTHON) scripts/busco_illumina.py
	@test -s results/busco/illumina/short_summary.specific.staphylococcus_odb12.2.illumina.txt
	@test -s results/busco/illumina/short_summary.specific.staphylococcus_odb12.2.illumina.json
	@test -s results/busco/illumina/run_staphylococcus_odb12.2/short_summary.txt
	@touch $@
	@echo "[OK] Illumina BUSCO evaluation completed and verified"
