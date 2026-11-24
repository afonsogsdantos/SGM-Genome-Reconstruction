# Bacterial Genome Reconstruction and Annotation

**Trabalho Prático 1 — Sequenciação de Genomas e Metagenómica**  
Faculdade de Ciências da Universidade do Porto (FCUP) · 2026/2027

## Autores

- Afonso Santos
- Rafael Santos

## Objetivos e estado do projeto

Reconstruir, avaliar e anotar o genoma de *Staphylococcus aureus* e comparar três estratégias: **Illumina-only**, **Nanopore-only** e **montagem híbrida**. A pipeline Illumina foi implementada e executada; as componentes Nanopore, híbrida, anotação e empacotamento final ainda estão em desenvolvimento.

## Dados

| Recurso | Acesso | Fonte |
|---|---|---|
| Reads Illumina paired-end | `SRR13745244` | European Nucleotide Archive (ENA) |
| Reads Oxford Nanopore | `SRR13745250` | ENA |
| Genoma de referência | `GCA_018093205.1` | NCBI |

Referência: *Staphylococcus aureus* strain CI/BAC/25/13/W, com cromossoma `CP071102.1` e plasmídeo `CP071103.1`, num total de **2 720 880 bp**.

## Requisitos e ambiente

O desenvolvimento e os testes da pipeline Illumina foram realizados em **Ubuntu no WSL (Windows)**, com **micromamba**. O ambiente é definido em [`environment.yml`](environment.yml).

| Programa | Versão observada nos testes |
|---|---|
| Python | 3.12.15 |
| FastQC | 0.12.1 |
| fastp | 0.24.3 |
| SPAdes | 4.3.0 |
| QUAST | 5.3.0 |
| BUSCO | 6.1.0 |

Para criar o ambiente, a partir da raiz do repositório:

```bash
micromamba create -f environment.yml -y
micromamba activate sgm
```

É necessária conectividade à Internet para os downloads iniciais (ENA, NCBI e dataset BUSCO) e espaço em disco para os dados e ficheiros temporários. A montagem Illumina utiliza quatro threads e `-m 8` no SPAdes (limite de memória em GB). Os scripts recorrem a diretórios temporários Linux, evitando incompatibilidades com espaços no caminho Windows do projeto.

## Estrutura do repositório

```text
.
├── Makefile
├── environment.yml
├── scripts/
│   ├── check_ena.py
│   ├── download_ena.py
│   ├── download_reference.py
│   ├── quality_control.py
│   ├── assemble_illumina.py
│   ├── evaluate_illumina.py
│   └── busco_illumina.py
├── data/                 # gerado, não versionado
│   ├── raw/
│   ├── cleaned/
│   └── reference/
├── results/              # gerado, não versionado
│   ├── qc/illumina/
│   ├── assemblies/illumina/
│   ├── quast/illumina/
│   └── busco/illumina/
├── report/
└── deliverables/         # reservado para entregáveis
```

Os reads, a referência e os resultados **não são incluídos no Git**. Os scripts voltam a obter os dados a partir dos acessos indicados.

## Execução Illumina

Ativar primeiro o ambiente `sgm`. Na raiz do projeto:

```bash
make illumina
```

O alvo `illumina` engloba downloads, controlo de qualidade, montagem e avaliação por QUAST e BUSCO. Também é possível executar etapas separadamente:

```bash
make download
make verify_downloads
make qc_illumina
make assemble_illumina
make quast_illumina
make busco_illumina
```

Os downloads dos FASTQ são verificados pelos MD5 fornecidos pelo ENA. As regras do Makefile usam marcadores `.complete` e verificam a presença e o tamanho não nulo dos principais ficheiros gerados.

### Controlo de qualidade — FastQC e fastp

O script [`scripts/quality_control.py`](scripts/quality_control.py) analisa os reads antes e depois da filtragem. O `fastp` usa trimming com janela deslizante de **4 bases**, qualidade média mínima **Q20**, comprimento mínimo de read **50 bp** e **4 threads**.

Resultados observados:

- **433 861 pares** de reads retidos (**87,83%** dos pares iniciais).
- Proporção de bases Q30 após filtragem: **93,76%** (aproximadamente).
- Reads filtrados: `data/cleaned/illumina_1.clean.fastq.gz` e `data/cleaned/illumina_2.clean.fastq.gz`.
- Relatórios: `results/qc/illumina/`.

### Montagem — SPAdes

O script [`scripts/assemble_illumina.py`](scripts/assemble_illumina.py) executa o **SPAdes 4.3.0** em modo `--isolate`, com **4 threads** e limite de **8 GB de RAM**, utilizando os reads filtrados.

Montagem principal: `results/assemblies/illumina/successful/contigs.fasta`.

Estatísticas sobre **todos** os contigs produzidos:

- **132 contigs**, total de **2 680 169 bp**;
- maior contig: **189 750 bp**.

### Avaliação estrutural — QUAST

O script [`scripts/evaluate_illumina.py`](scripts/evaluate_illumina.py) avalia a montagem contra a referência `GCA_018093205.1`, com `--min-contig 500`, `--no-icarus` e **4 threads**.

| Métrica QUAST | Resultado |
|---|---:|
| Contigs ≥ 500 bp | 118 |
| Comprimento total dos contigs ≥ 500 bp | 2 676 125 bp |
| Maior contig | 189 750 bp |
| N50 | 58 553 bp |
| L50 | 16 |
| Genome fraction | 98,294% |
| Misassemblies | 0 |
| Local misassemblies | 1 |
| Mismatches por 100 kbp | 2,95 |
| Indels por 100 kbp | 2,02 |

A *genome fraction* é a percentagem da sequência de referência coberta pelos alinhamentos; **não equivale à completude dos genes conservados**. Os valores QUAST usam o limiar de contigs indicado e podem diferir das estatísticas referentes a todos os contigs.

Relatórios: `results/quast/illumina/`, incluindo `report.txt`, `report.tsv` e `report.html`.

### Completude genética — BUSCO

O script [`scripts/busco_illumina.py`](scripts/busco_illumina.py) executa **BUSCO 6.1.0**, modo `genome`, com **4 threads**, usando o dataset **`staphylococcus_odb12.2`** (data de criação: **2026-05-22**; **1317** grupos BUSCO). A predição de genes foi realizada com Prodigal.

```text
C:98.9%[S:98.6%,D:0.2%],F:0.1%,M:1.1%,n:1317
```

| Categoria BUSCO | Grupos |
|---|---:|
| Completos (C) | 1302 |
| Completos em cópia única (S) | 1299 |
| Completos duplicados (D) | 3 |
| Fragmentados (F) | 1 |
| Ausentes (M) | 14 |

Estes resultados mostram elevada recuperação de genes conservados esperados para a linhagem selecionada. Um BUSCO classificado como ausente não demonstra, por si só, ausência biológica do gene.

Relatórios: `results/busco/illumina/`. O dataset descarregado é guardado numa cache local em `~/.cache/sgm_busco/`.

## Limitações e próximos passos

- **A execução Illumina com os resultados já existentes foi validada** com `make illumina`, incluindo verificações dos ficheiros principais; **a reconstrução integral a partir de um ambiente limpo ainda não foi testada**.
- Alterações ao `environment.yml` não obrigam, por si só, à repetição das análises já marcadas como completas. Para comparar novas versões das ferramentas, é necessário gerir explicitamente a reconstrução.
- Se um ficheiro de saída desaparecer mas o marcador `.complete` persistir, a verificação pode detetar o problema sem o reconstruir automaticamente.
- Ainda faltam: pipeline Nanopore-only, montagem híbrida, anotação, comparação das três abordagens, relatório científico e empacotamento/teste com Apptainer. **Não há ainda uma imagem Apptainer funcional neste repositório.**

## Desenvolvimento e integração

O desenvolvimento usa branches Git separadas:

- `main`: base de integração;
- `feat/illumina`: trabalho Illumina;
- `feat/nanopore`: trabalho Nanopore, a preparar.

As alterações serão integradas depois de revistas e testadas. A automação de execução final e os entregáveis serão atualizados à medida que as restantes componentes forem implementadas.
