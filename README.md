# llm-vuln-detection-ablation

Reproduction artefacts for the paper:

> **Toward Practical LLM-assisted Vulnerability Detection: A Specificity-Aware Ablation Study with Hint-Leakage Controls**
> Hsin-Lei Lin¹, Hung-En Kao², Shih-Ming Pi¹, Kuo-Chen Li¹
> ¹ Department of Information Management, College of Business, Chung Yuan Christian University, Taoyuan, Taiwan
> ² Ph.D. Program in Business, College of Business, Chung Yuan Christian University, Taoyuan, Taiwan
> *Manuscript under review (2026).*

This repository contains the dataset curation, experimental, and analysis pipelines that produce every quantitative result reported in the paper, including all metric tables, figure data, and the qualitative case study list.

---

## Contents

```
llm-vuln-detection-ablation/
├── README.md                        This file.
├── LICENSE                          Dual license: MIT (code) AND CC BY 4.0 (data).
├── CITATION.cff                     Machine-readable citation metadata.
├── requirements.txt                 Python dependencies.
├── .gitignore                       Standard Python and Jupyter ignores.
│
├── notebooks/                       Ten Jupyter notebooks. Run 01-07 in order; 08-10 are the CWE-98 boundary-condition study.
│   ├── 01_dataset_curation.ipynb        Curate 234 PHP samples from NIST SARD.
│   ├── 02_run_ablation_hinted.ipynb     RQ1: 5 HINTED prompt variants on GPT-4o-mini.
│   ├── 03_run_ablation_clean.ipynb      RQ2: Variants C and E re-run with category-agnostic prompts.
│   ├── 04_run_cross_generation.ipynb    RQ3: Variant C HINTED on GPT-3.5-turbo, 100-sample subset.
│   ├── 05_metrics_and_figures.ipynb     Compute all paper tables and figure data from the result CSVs.
│   ├── 06_run_frontier_validation.ipynb RQ4: run Variants A and E on frontier model GPT-5.5 (234 samples).
│   ├── 07_frontier_stats.ipynb          RQ4: self-contained; reproduces Table 3 from the GPT-5.5 CSV.
│   ├── 08_cwe95_generalization.ipynb    Exploratory CWE-95 probe (floor effect; not used in final analysis).
│   ├── 09_cwe98_generalization_gpt55.ipynb  CWE-98 boundary condition on GPT-5.5 (ceiling effect).
│   └── 10_cwe98_floor_gpt4omini.ipynb   CWE-98 boundary condition on GPT-4o-mini (floor effect).
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
├── data/                            Canonical file lists and frontier-validation results.
│   ├── file_list_234.txt                234 samples used in RQ1 and RQ2.
│   ├── file_list_100_stratified.txt     100 samples used in RQ3 (subset of file_list_234.txt).
│   ├── rq4_frontier_gpt55.csv           Committed copy of the RQ4 GPT-5.5 predictions (234 rows).
│   ├── file_list_cwe98.txt              144-sample CWE-98 boundary-condition test set (96 vuln + 48 safe).
│   ├── cwe98_generalization_gpt55.csv   CWE-98 per-sample predictions, GPT-5.5, four conditions.
│   └── cwe98_floor_gpt4omini.csv        CWE-98 per-sample predictions, GPT-4o-mini, four conditions.
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
    ├── rq4_frontier_gpt55.csv            (also committed to data/ for archival)
    └── case_study_discordant_cmdinj.csv
```

---

## Quickstart

### Prerequisites

- Python 3.10 or higher
- An OpenAI API key with access to `gpt-4o-mini` and `gpt-3.5-turbo` (and `gpt-5.5` for the optional RQ4 frontier validation)
- Approximately USD 0.20 in OpenAI credits and 1.5 hours of runtime to reproduce the core GPT-4o-mini and GPT-3.5-turbo experiments (RQ1–RQ3); the optional RQ4 frontier validation on GPT-5.5 adds approximately USD 4.92

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

The RQ4 frontier validation (notebooks `06` and `07`) is optional and documented in its own section below.

### Verify reproduction

After running notebook `05`, the printed numbers should match the paper's Table 1, Table 2, Figures 1–4, and the headline statistics in Sections 4.1, 4.3, and 5.1. Note that small differences (typically ±2–3 samples per variant) are expected because GPT-4o-mini at `temperature=0.1` is not deterministic.

To verify the RQ4 frontier-validation results (Table 3), run `notebooks/07_frontier_stats.ipynb`. Unlike the core experiments, this step is fully deterministic: it recomputes every value in Table 3 from the committed `data/rq4_frontier_gpt55.csv` and requires no API access.

---

## Paper-to-repository cross-reference

| Paper element | Reproduce by running |
|---|---|
| Table 1 (seven-variant performance) | `05_metrics_and_figures.ipynb` Section 2 |
| §4.1 main McNemar test (χ² = 12.97, p = 0.0003) | `05_metrics_and_figures.ipynb` Section 3 |
| Figure 2 (per-CWE breakdown) | `05_metrics_and_figures.ipynb` Section 4 |
| Table 2 (paired HINTED vs CLEAN McNemar) | `05_metrics_and_figures.ipynb` Section 5 |
| §4.3 cross-generation (98/100 Safe predictions) | `05_metrics_and_figures.ipynb` Section 6 |
| §4.5 / Table 3 frontier validation (GPT-5.5, McNemar χ² = 15.06) | `07_frontier_stats.ipynb` |
| §5.1 30 discordant CmdInj cases | `05_metrics_and_figures.ipynb` Section 7 |
| Figures 1–4 numeric data | `05_metrics_and_figures.ipynb` Section 8 |

---

## RQ4 — Frontier-Model Validation (GPT-5.5)

To test whether the Instruction Overload effect is specific to limited-capacity models, we replicated the Baseline (Variant A) vs Full-Framework (Variant E, HINTED) contrast on a frontier model, **GPT-5.5** (snapshot `gpt-5.5-2026-04-23`), over the full 234-sample benchmark (100 CWE-78, 100 CWE-89, 34 Safe). This corresponds to **Section 4.5 / Table 3** of the paper.

- `notebooks/06_run_frontier_validation.ipynb` runs Variants A and E on GPT-5.5 and writes per-sample predictions to `workspace/results/rq4_frontier_gpt55.csv` (the `workspace/` tree is git-ignored). A copy of this output is committed to the repository at `data/rq4_frontier_gpt55.csv` for archival and review. Requires an OpenAI API key with GPT-5.5 access (read from the `OPENAI_API_KEY` environment variable, or entered interactively; never stored).
- `notebooks/07_frontier_stats.ipynb` is **self-contained**: it reads only `data/rq4_frontier_gpt55.csv` and reproduces every value in Table 3 (Recall, Specificity, F1, Accuracy, per-CWE recall, and both McNemar tests). No API key or network access required.
- `data/rq4_frontier_gpt55.csv` holds the per-sample predictions (234 rows: `File_Name, True_Label, True_CWE, Variant_A_Baseline, Variant_E_Full`).

**Key result:** the full framework induces a statistically significant, perfectly one-directional shift toward conservative (Safe) verdicts (paired-prediction McNemar χ² = 15.06, p = 0.0001; all 17 discordant verdicts move Vulnerable → Safe), confirming that Instruction Overload is not a small-model artefact. Its net effect on classification correctness is not significant (correctness McNemar χ² = 0.94, p = 0.332), as the suppression removes both true and false positives.

---

## CWE-98 Boundary-Condition Experiment (File Inclusion)

To test whether the prompt-structural effects observed on the primary benchmark (CWE-78 / CWE-89) generalise across a third, mechanistically distinct vulnerability class **and** across model capability, we constructed an independent CWE-98 (PHP File Inclusion) test set and evaluated four prompt conditions on two models spanning the capability range. This corresponds to **Sections 4.6 and 5.4** of the paper.

### Test set

- **144 samples**: 96 vulnerable (`no_sanitizing` variants, stratified across 16 input sources) + 48 safe (stratified by source). The larger safe stratum, relative to the primary benchmark, gives a more robust estimate of Specificity.
- Sample identities are published in `data/file_list_cwe98.txt` (paths relative to the CWE-98 dataset root, mirroring the SARD filename convention). As with the primary benchmark, the underlying `.php` files are drawn from the NIST SARD PHP Vulnerability Test Suite and are **not** redistributed here.

### Conditions and models

Four conditions — Baseline (A), Patterns-CLEAN (C), Full-CLEAN (E), and a Full-HINTED variant naming only CWE-98 — were each run on:

- **GPT-4o-mini** (`temperature = 0.1`) — `notebooks/10_cwe98_floor_gpt4omini.ipynb`, output `data/cwe98_floor_gpt4omini.csv`.
- **GPT-5.5** (`gpt-5.5-2026-04-23`, default temperature; the API does not accept a custom value) — `notebooks/09_cwe98_generalization_gpt55.ipynb`, output `data/cwe98_generalization_gpt55.csv`.

The CWE-98 prompts are defined inline within notebooks 09 and 10 (the HINTED condition names only CWE-98), so these notebooks are self-contained with respect to prompt definitions.

### Key result: a capability-difficulty boundary condition

| Model | Regime | Behaviour |
|---|---|---|
| GPT-4o-mini | **Floor effect** | Over-flagging saturates: the Baseline judges all 144 samples Vulnerable; only 4/144 rows differ across the four conditions, so prompt-structural effects are unmeasurable. |
| GPT-5.5 | **Ceiling effect** | Near-perfect even when unstructured: the Baseline already attains F1 around 0.98; only 12/144 rows differ, and the Instruction Overload / hint-leakage contrasts are directionally consistent but statistically negligible. |

The prompt-structural effects of the primary study are therefore **not universal** but are interaction effects between model capability and task difficulty, observable only in an intermediate regime where the model is strained but not saturated.

### Exploratory note: CWE-95

`notebooks/08_cwe95_generalization.ipynb` documents an earlier attempt to use CWE-95 (Eval Injection) as the third class. It is retained for transparency: GPT-4o-mini exhibited a total floor effect on CWE-95 (every sample judged Vulnerable under all conditions), so CWE-95 could not serve as a measurable generalisation test, and CWE-98 was selected instead.

---

## Notes for reviewers

- **Sample selection.** The 234-sample composition is recorded in `data/file_list_234.txt`, which is the canonical specification. The curation pipeline in `01_dataset_curation.ipynb` extracts candidate samples by filename pattern from the public SARD corpus and intersects them with this list. The list and the pipeline together guarantee that any reviewer reproduces the same 234 samples used in the paper.
- **Variant naming.** The paper uses `Variant_B_Persona`. The original experimental codebase used the placeholder `Variant_B_PERFECT`; the repository renames it to align with the paper. Prompt content is unchanged.
- **CWE-79 (XSS) is out of scope.** XSS samples were targeted during early exploration but excluded for the reasons documented in `docs/cwe79_absence_evidence.txt` and Section 3.1.3 of the paper. The XSS audit folder under the curated dataset is empty by design.
- **Stochasticity caveat.** GPT-4o-mini and GPT-3.5-turbo at `temperature=0.1` are not strictly deterministic. Re-running the experiments will produce metric values within approximately ±2–3 samples per variant of those reported in the paper. The qualitative findings (Instruction Overload, Answer Leakage, Cognitive Threshold) are robust under this variation.
- **Frontier validation reproducibility.** Notebook `07_frontier_stats.ipynb` is fully deterministic: it recomputes Table 3 from the committed `data/rq4_frontier_gpt55.csv` and requires no API access. Re-running the generation step (`06`) against the live GPT-5.5 endpoint is subject to the same stochasticity caveat as the other experiments.
- **Cost transparency.** The full GPT-4o-mini / GPT-3.5-turbo pipeline costs approximately USD 0.20 on the OpenAI API at the prices in effect at the time of writing. The RQ4 frontier validation on GPT-5.5 cost approximately USD 4.92.

---

## Licensing

- **Code** (`notebooks/`, any `.py` files): released under the MIT License.
- **Data, prompts, file lists, and result CSVs** (`prompts/`, `data/`, any output `.csv` produced by these notebooks): released under the Creative Commons Attribution 4.0 International License, CC BY 4.0.

Both licenses are provided in the single `LICENSE` file at the repository root, with an SPDX header (`SPDX-License-Identifier: MIT AND CC-BY-4.0`) and explicit per-section coverage.

The PHP source samples themselves are **not** redistributed by this repository. They are obtained at runtime by cloning the public NIST SARD PHP Vulnerability Test Suite under its original license. See https://github.com/stivalet/PHP-Vulnerability-test-suite for the source corpus.

---

## Citation

If you use this repository or the underlying paper in your work, please cite:

```
Hsin-Lei Lin, Hung-En Kao, Shih-Ming Pi, Kuo-Chen Li (2026).
"Toward Practical LLM-assisted Vulnerability Detection: A Specificity-Aware
Ablation Study with Hint-Leakage Controls."
Manuscript under review, 2026.
```

A machine-readable citation is provided in `CITATION.cff`.

---

## Contact

For questions about the experiments or the repository, contact Hung-En Kao (corresponding author) via the contact information in the paper.
