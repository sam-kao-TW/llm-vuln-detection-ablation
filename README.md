# llm-vuln-detection-ablation

Reproduction artefacts for the paper:

> **Toward Practical LLM-assisted Vulnerability Detection: Design Principles and Framework for Web Application Security**
> Hsin-Lei Lin, Hung-En Kao, Shih-Ming Pi, Kuo-Chen Li
> Department of Information Management, Chung Yuan Christian University
> *Under review at Journal of Systems and Software (May 2026).*

This repository contains the dataset curation, experimental, and analysis pipelines that produce every quantitative result reported in the paper, including all metric tables, figure data, and the qualitative case study list.

---

## Contents

```
llm-vuln-detection-ablation/
├── README.md                        This file.
├── LICENSE-CODE                     MIT License (covers all code).
├── LICENSE-DATA                     CC BY 4.0 (covers prompts, file lists, results CSVs).
├── CITATION.cff                     Machine-readable citation metadata.
├── requirements.txt                 Python dependencies.
├── .gitignore                       Standard Python and Jupyter ignores.
│
├── notebooks/                       Five Jupyter notebooks. Run in order.
│   ├── 01_dataset_curation.ipynb        Curate 234 PHP samples from NIST SARD.
│   ├── 02_run_ablation_hinted.ipynb     RQ1: 5 HINTED prompt variants on GPT-4o-mini.
│   ├── 03_run_ablation_clean.ipynb      RQ2: Variants C and E re-run with category-agnostic prompts.
│   ├── 04_run_cross_generation.ipynb    RQ3: Variant C HINTED on GPT-3.5-turbo, 100-sample subset.
│   └── 05_metrics_and_figures.ipynb     Compute all paper tables and figure data from the result CSVs.
│
├── prompts/                         Eight prompt files (one per variant + system message).
│   ├── system_message.txt
│   ├── variant_A_baseline.txt
│   ├── variant_B_persona.txt
│   ├── variant_C_patterns_hinted.txt
│   ├── variant_C_patterns_clean.txt
│   ├── variant_D_cot.txt
│   ├── variant_E_full_hinted.txt
│   └── variant_E_full_clean.txt
│
├── data/                            Canonical file lists committed to the repository.
│   ├── file_list_234.txt                234 samples used in RQ1 and RQ2.
│   └── file_list_100_stratified.txt     100 samples used in RQ3 (subset of file_list_234.txt).
│
├── docs/                            Supplementary documentation.
│   └── cwe79_absence_evidence.txt       Audit log confirming the empty CWE-79 (XSS) folder
│                                        referenced in Section 3.1.3 of the paper.
│
└── figures/                         Source files for the four paper figures (drawio + exported PNG).
    ├── Figure1_F1_vs_Specificity.drawio    Figure1_F1_vs_Specificity.png
    ├── Figure2_CWE_subgroup.drawio          Figure2_CWE_subgroup.png
    ├── Figure3_HINTED_vs_CLEAN.drawio       Figure3_HINTED_vs_CLEAN.png
    └── Figure4_TwoSided_Failure.drawio      Figure4_TwoSided_Failure.png
```

After the notebooks are run, the following directory is created (excluded from the repository by `.gitignore`):

```
workspace/
├── raw_sard_php/                    Cloned PHP Vulnerability Test Suite (~7 MB, 42k files).
├── final_dataset/                   234 curated samples organised by category.
└── results/                         Output CSVs from notebooks 02–05.
    ├── rq1_ablation_results_hinted.csv
    ├── rq2_ablation_results_clean.csv
    ├── rq3_cross_generation_gpt35.csv
    └── case_study_discordant_cmdinj.csv
```

---

## Quickstart

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key with access to `gpt-4o-mini` and `gpt-3.5-turbo`
- Approximately USD 0.20 in OpenAI credits and 1.5 hours of runtime to reproduce all experiments

### Installation

```bash
git clone https://github.com/<your-handle>/llm-vuln-detection-ablation.git
cd llm-vuln-detection-ablation
pip install -r requirements.txt
```

### Run the pipeline

Set your OpenAI API key once per shell session:

```bash
export OPENAI_API_KEY=sk-...
```

Then launch Jupyter and run the notebooks in order from the repository root:

```bash
jupyter lab
```

Open and run all cells in:

1. `notebooks/01_dataset_curation.ipynb` — produces `workspace/final_dataset/` (one-time, ~2 minutes)
2. `notebooks/02_run_ablation_hinted.ipynb` — produces `rq1_ablation_results_hinted.csv` (~30–45 minutes)
3. `notebooks/03_run_ablation_clean.ipynb` — produces `rq2_ablation_results_clean.csv` (~12–18 minutes)
4. `notebooks/04_run_cross_generation.ipynb` — produces `rq3_cross_generation_gpt35.csv` (~5–10 minutes)
5. `notebooks/05_metrics_and_figures.ipynb` — prints all paper tables and figure data, writes `case_study_discordant_cmdinj.csv`

All notebooks support resume-on-interrupt: re-running a partially completed notebook will pick up from the last saved sample.

### Verify reproduction

After running notebook `05`, the printed numbers should match the paper's Table 1, Table 2, Figures 1–4, and the headline statistics in Sections 4.1, 4.3, and 5.1. Note that small differences (typically ±2–3 samples per variant) are expected because GPT-4o-mini at `temperature=0.1` is not deterministic.

---

## Paper-to-repository cross-reference

| Paper element | Reproduce by running |
|---|---|
| Table 1 (seven-variant performance) | `05_metrics_and_figures.ipynb` Section 2 |
| §4.1 main McNemar test (χ² = 12.97, p = 0.0003) | `05_metrics_and_figures.ipynb` Section 3 |
| Figure 2 (per-CWE breakdown) | `05_metrics_and_figures.ipynb` Section 4 |
| Table 2 (paired HINTED vs CLEAN McNemar) | `05_metrics_and_figures.ipynb` Section 5 |
| §4.3 cross-generation (98/100 Safe predictions) | `05_metrics_and_figures.ipynb` Section 6 |
| §5.1 30 discordant CmdInj cases | `05_metrics_and_figures.ipynb` Section 7 |
| Figures 1–4 numeric data | `05_metrics_and_figures.ipynb` Section 8 |

---

## Notes for reviewers

- **Sample selection.** The 234-sample composition is recorded in `data/file_list_234.txt`, which is the canonical specification. The curation pipeline in `01_dataset_curation.ipynb` extracts candidate samples by filename pattern from the public SARD corpus and intersects them with this list. The list and the pipeline together guarantee that any reviewer reproduces the same 234 samples used in the paper.

- **Variant naming.** The paper uses `Variant_B_Persona`. The original experimental codebase used the placeholder `Variant_B_PERFECT`; the repository renames it to align with the paper. Prompt content is unchanged.

- **CWE-79 (XSS) is out of scope.** XSS samples were targeted during early exploration but excluded for the reasons documented in `docs/cwe79_absence_evidence.txt` and Section 3.1.3 of the paper. The XSS audit folder under the curated dataset is empty by design.

- **Stochasticity caveat.** GPT-4o-mini and GPT-3.5-turbo at `temperature=0.1` are not strictly deterministic. Re-running the experiments will produce metric values within approximately ±2–3 samples per variant of those reported in the paper. The qualitative findings (Instruction Overload, Answer Leakage, Cognitive Threshold) are robust under this variation.

- **Cost transparency.** The full pipeline costs approximately USD 0.20 on the OpenAI API at the prices in effect at the time of writing.

---

## Licensing

- **Code** (`notebooks/`, any `.py` files): released under the MIT License (`LICENSE-CODE`).
- **Data, prompts, file lists, and result CSVs** (`prompts/`, `data/`, any output `.csv` produced by these notebooks): released under the Creative Commons Attribution 4.0 International License, CC BY 4.0 (`LICENSE-DATA`).

The PHP source samples themselves are **not** redistributed by this repository. They are obtained at runtime by cloning the public NIST SARD PHP Vulnerability Test Suite under its original license. See https://github.com/stivalet/PHP-Vulnerability-test-suite for the source corpus.

---

## Citation

If you use this repository or the underlying paper in your work, please cite:

```
Hsin-Lei Lin, Hung-En Kao, Shih-Ming Pi, Kuo-Chen Li (2026).
"Toward Practical LLM-assisted Vulnerability Detection: Design Principles and
Framework for Web Application Security."
Under review at Journal of Systems and Software, May 2026.
```

A machine-readable citation is provided in `CITATION.cff`.

---

## Contact

For questions about the experiments or the repository, contact Hung-En Kao (corresponding author) via the contact information in the paper.
