#!/usr/bin/env python3

import json
from urllib.request import urlopen
from urllib.parse import urlencode

# Identificadores dos dados de sequenciacao
ACCESSIONS = ["SRR13745244", "SRR13745250"]

# API do European Nucleotide Archive
BASE_URL = "https://www.ebi.ac.uk/ena/portal/api/filereport"

for accession in ACCESSIONS:

    # Parametros da consulta
    params = urlencode({
        "accession": accession,
        "result": "read_run",
        "fields": "run_accession,library_strategy,library_layout,instrument_platform,fastq_ftp",
        "format": "json"
    })

    url = f"{BASE_URL}?{params}"

    print(f"\nChecking {accession}...")

    # Consultar a API
    with urlopen(url, timeout=60) as response:
        records = json.load(response)

    # Verificar se existem resultados
    if not records:
        raise RuntimeError(
            f"No ENA records found for {accession}"
        )

    record = records[0]

    # Mostrar informacoes
    print("Platform:", record.get("instrument_platform"))
    print("Layout:", record.get("library_layout"))
    print("FASTQ files:")

    for filepath in record.get("fastq_ftp", "").split(";"):
        if filepath:
            print(" -", filepath)
