#!/usr/bin/env python3

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ACCESSION = "GCA_018093205.1"
OUTPUT = Path("data/reference/reference.fasta")


def get_datasets_command():
    executable = shutil.which("datasets")

    if executable:
        return executable

    local = Path.home() / ".local/bin/datasets"

    if local.is_file():
        return str(local)

    raise RuntimeError("NCBI Datasets is not installed")


def valid_fasta(path):
    if not path.is_file() or path.stat().st_size == 0:
        return False

    with path.open("rb") as file:
        for line in file:
            if line.strip():
                return line.startswith(b">")

    return False


def download_reference():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if valid_fasta(OUTPUT):
        print(f"[OK] Reference already exists: {OUTPUT}")
        return

    datasets = get_datasets_command()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "reference.zip"

        command = [
            datasets,
            "download",
            "genome",
            "accession",
            ACCESSION,
            "--include",
            "genome",
            "--filename",
            str(archive),
        ]

        print(f"[DOWNLOAD] Reference {ACCESSION}", flush=True)

        subprocess.run(command, check=True)

        with zipfile.ZipFile(archive) as zip_file:
            fasta_files = [
                name for name in zip_file.namelist()
                if name.startswith(
                    f"ncbi_dataset/data/{ACCESSION}/"
                ) and name.endswith((".fna", ".fasta"))
            ]

            if len(fasta_files) != 1:
                raise RuntimeError(
                    "Expected exactly one reference FASTA, "
                    f"found {len(fasta_files)}"
                )

            temporary_output = OUTPUT.with_name(
                OUTPUT.name + ".part"
            )

            with zip_file.open(fasta_files[0]) as source:
                with temporary_output.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

            if not valid_fasta(temporary_output):
                temporary_output.unlink(missing_ok=True)
                raise RuntimeError("Invalid reference FASTA")

            temporary_output.replace(OUTPUT)

    print(f"[OK] Reference saved: {OUTPUT}", flush=True)


if __name__ == "__main__":
    download_reference()
