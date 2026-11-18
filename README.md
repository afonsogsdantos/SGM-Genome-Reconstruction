# Bacterial Genome Reconstruction and Annotation

Trabalho Pratico 1 - Sequenciacao de Genomas e Metagenomica
2026/2027 - FCUP

## Autores

- Afonso Santos
- Rafael Santos

## Objetivo

Reconstruir e anotar o genoma de Staphylococcus aureus,
comparando tres abordagens:

1. Illumina-only
2. Nanopore-only
3. Hybrid assembly

## Dados

- Illumina: SRR13745244
- Nanopore: SRR13745250
- Referencia: GCA_018093205.1

## Estrutura

- data/: dados de sequenciacao e referencia
- scripts/: scripts de automacao e analise
- results/: resultados intermédios
- report/: codigo-fonte do relatorio
- deliverables/: ficheiros finais gerados

## Execucao

A pipeline sera executada automaticamente com:

    apptainer build workflow.sif workflow.def
    apptainer run workflow.sif

A implementacao encontra-se em desenvolvimento.
