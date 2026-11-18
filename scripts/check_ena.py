#!/usr/bin/env python3

import json
from urllib.request import urlopen
from urllib.parse import urlencode

ACCESSIONS = ["SRR13745244", "SRR13745250"]

BASE_URL = "https://www.ebi.ac.uk/ena/portal/api/filereport"

for accession in ACCESSIONS:

    params = urlencode({
        "accession": accession,
        "result": "read_run",
        "fields": (
            "run_accession,library_layout,"
            "instrument_platform,fastq_ftp,"
            "fastq_md5,fastq_bytes"
        ),
        "format": "json"
    })

    url = f"{BASE_URL}?{params}"

    print(f"\n{'=' * 50}")
    print(f"Checking {accession}")
    print("=" * 50)

    with urlopen(url, timeout=60) as response:
        records = json.load(response)

    if len(records) != 1:
        raise RuntimeError(
            f"Expected one ENA record for {accession}, "
            f"found {len(records)}"
        )

    record = records[0]

    print("Platform:", record.get("instrument_platform"))
    print("Layout:", record.get("library_layout"))

    files = record.get("fastq_ftp", "").split(";")
    md5s = record.get("fastq_md5", "").split(";")
    sizes = record.get("fastq_bytes", "").split(";")

    if not files or not files[0]:
        raise RuntimeError(
            f"No FASTQ files available for {accession}"
        )

    if not (len(files) == len(md5s) == len(sizes)):
        raise RuntimeError(
            f"Inconsistent FASTQ metadata for {accession}"
        )

    for i, (filepath, md5, size) in enumerate(
        zip(files, md5s, sizes), start=1
    ):
        print(f"\nFile {i}:")
        print("URL:", "https://" + filepath)
        print("Size (bytes):", size)
        print("MD5:", md5)
