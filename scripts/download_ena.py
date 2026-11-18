#!/usr/bin/env python3

import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, urlretrieve

ACCESSIONS = {
    "SRR13745244": ["illumina_1.fastq.gz", "illumina_2.fastq.gz"],
    "SRR13745250": ["nanopore.fastq.gz"],
}

BASE_URL = "https://www.ebi.ac.uk/ena/portal/api/filereport"
OUTPUT_DIR = Path("data/raw")
MAX_ATTEMPTS = 3


def get_metadata(accession):
    params = urlencode({
        "accession": accession,
        "result": "read_run",
        "fields": "run_accession,fastq_ftp,fastq_md5,fastq_bytes",
        "format": "json",
    })

    with urlopen(f"{BASE_URL}?{params}", timeout=60) as response:
        records = json.load(response)

    if len(records) != 1 or records[0].get("run_accession") != accession:
        raise RuntimeError(f"Invalid ENA response for {accession}")

    record = records[0]

    urls = record["fastq_ftp"].split(";")
    md5s = record["fastq_md5"].split(";")
    sizes = record["fastq_bytes"].split(";")

    if not (
        len(urls) == len(md5s) == len(sizes)
        == len(ACCESSIONS[accession])
    ):
        raise RuntimeError(f"Incomplete metadata for {accession}")

    return list(zip(urls, md5s, sizes))


def calculate_md5(path):
    digest = hashlib.md5()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def valid_file(path, expected_md5, expected_size):
    if not path.is_file():
        return False

    if path.stat().st_size != int(expected_size):
        return False

    return calculate_md5(path) == expected_md5.lower()


def download_file(url, destination, expected_md5, expected_size):
    if valid_file(destination, expected_md5, expected_size):
        print(f"[OK] Already verified: {destination}", flush=True)
        return

    temporary = destination.with_name(destination.name + ".part")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            temporary.unlink(missing_ok=True)

            print(
                f"[DOWNLOAD] {destination.name} "
                f"(attempt {attempt}/{MAX_ATTEMPTS})",
                flush=True,
            )

            urlretrieve(url, temporary)

            if not valid_file(temporary, expected_md5, expected_size):
                raise RuntimeError("Size or MD5 verification failed")

            temporary.replace(destination)
            print(f"[OK] Verified: {destination}", flush=True)
            return

        except Exception as error:
            print(f"[ERROR] {error}", flush=True)
            temporary.unlink(missing_ok=True)

            if attempt == MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Could not download {destination.name}"
                ) from error

            time.sleep(3 * attempt)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for accession, filenames in ACCESSIONS.items():
        print(f"\nProcessing {accession}", flush=True)

        metadata = get_metadata(accession)

        for (ftp_path, md5, size), filename in zip(metadata, filenames):
            url = "https://" + ftp_path.removeprefix("https://")
            destination = OUTPUT_DIR / filename

            download_file(url, destination, md5, size)

    print("\nAll sequencing files downloaded and verified!")


if __name__ == "__main__":
    main()
