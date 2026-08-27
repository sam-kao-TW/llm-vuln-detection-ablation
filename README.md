# LLM-Assisted PHP Vulnerability Detection — Ablation Study (Replication Package)

Replication package for the paper:

> **Capability Thresholds and Sanitisation Blind Spots in LLM-Assisted Vulnerability Detection: A Factorial Prompt Study on a Reconstructed PHP Benchmark**

This repository contains the reconstructed benchmark, all prompt definitions, the
experiment code, the per-sample model responses, the analysis tables, and the
figure-generation scripts needed to reproduce every result and figure in the paper.

- **Archived release:** https://doi.org/10.5281/zenodo.20192267
- **Source:** https://github.com/sam-kao-TW/llm-vuln-detection-ablation

---

## 1. What this study evaluates

A fully crossed 5 × 2 prompt factorial — five structural prompt variants
(Baseline, Persona, Patterns, Chain-of-Thought, Full Framework), each in a
CLEAN and a category-naming (HINTED) form — evaluated on a balanced
360-sample PHP benchmark spanning OS command injection (CWE-78), SQL
injection (CWE-89) and PHP remote file inclusion (CWE-98). Three model
generations are compared on the identical benchmark: GPT-3.5-turbo,
GPT-4o-mini and GPT-5.5.

## 2. Benchmark reconstruction and the two defects it corrects

The benchmark used here was rebuilt from scratch during revision, after two
defects were identified in the construction used in the original submission.
Both are corrected in this package.

**Defect 1 — inverted labels.** The earlier pipeline derived each sample's
ground-truth label from the name of its parent directory. Because the SARD PHP
test suite splits every category into `safe/` and `unsafe/` subdirectories, and
the filesystem traversal order placed the `safe/` split first, the samples
intended to be "vulnerable" were in fact all drawn from the safe split. Labels
are now assigned programmatically and verified against the SARD partition for
every sample.

**Defect 2 — ground truth leaked into the model input.** Every file in the SARD
PHP suite begins with a descriptive comment header that states `Safe sample` or
`Unsafe sample`. The earlier pipeline passed the raw file text to the model,
placing the answer in the prompt alongside the question. The runner now strips
this header and the copyright block before the code reaches the model (see
`strip_header` in `vulnbench.py`); notebook 01 additionally scans all 360
cleaned samples to confirm no leakage string remains.

The reconstructed benchmark is balanced (180 vulnerable / 180 safe; 60 + 60 per
CWE class), structurally deduplicated (360/360 unique by body hash), drawn with
a fixed stratified seed, and label-verified against the SARD `safe/` vs
`unsafe/` partition.

## 3. Repository contents

```
.
├── vulnbench.py                          # shared runner: prompts, header stripping, experiment loop
├── README.md
├── CITATION.cff
├── LICENSE
│
├── data/
│   ├── benchmark_360_metadata.csv        # 360 samples: id, path, cwe, source, sanitizer, sink, label, hash
│   ├── file_list_360.txt                 # the exact file list defining the benchmark
│   ├── main_4omini.csv                   # per-sample responses, GPT-4o-mini (3600 rows)
│   ├── crossgen_gpt35.csv                # per-sample responses, GPT-3.5-turbo (3600 rows)
│   ├── frontier_gpt55.csv                # per-sample responses, GPT-5.5 (3600 rows, 10 conditions)
│   ├── drift_check_A_clean.csv           # Baseline replicated on 48 samples after the final session
│   ├── stability_merged_3runs.csv        # GPT-5.5 three-run stability, merged (288 rows)
│   ├── TABLE1_full_metrics.csv           # full metric set, ten conditions x three models (30 rows)
│   ├── TABLE2_pairwise_mcnemar_floored.csv  # pairwise McNemar on the saturated models (90 rows)
│   ├── TABLE2_gpt55_pairwise_mcnemar.csv    # the 45 pairwise contrasts on GPT-5.5
│   ├── TABLE2_all_models_pairwise.csv       # the three models combined (135 rows)
│   ├── TABLE3_gpt55_AvsE.csv             # GPT-5.5 Baseline vs Full Framework, stratified
│   ├── TABLE3_component_attribution.csv  # each component vs Baseline; naming within each variant
│   ├── TABLE4_gpt55_by_sanitizer_mechanism.csv  # safe-sample accuracy by mechanism (see note below)
│   ├── TABLE4_blindspot_all_conditions.csv      # the type-level vs escaping gap under all ten conditions
│   └── TABLE5_capability_spectrum.csv    # capability spectrum across the three model generations
│
├── notebooks/
│   ├── 01_verify_benchmark.ipynb         # existence + label-integrity + leakage check (no API calls)
│   ├── 02_run_main_ablation.ipynb        # GPT-4o-mini, full 5x2 factorial (10 conditions)
│   ├── 03_run_crossgen_frontier.ipynb    # GPT-3.5-turbo (10 conditions) + GPT-5.5 (Baseline vs Full)
│   ├── 04_run_repeated.ipynb             # GPT-5.5 three-run stability on a 48-sample subset
│   ├── 05_complete_gpt55_factorial.ipynb # the eight remaining GPT-5.5 conditions + drift check
│   └── 06_stats_full_factorial.ipynb     # all statistics on the completed factorial (no API calls)
│
├── scripts/
│   ├── build_table1_all_models.py        # rebuilds TABLE1 from the three per-sample response files
│   └── build_table4_mechanism.py         # rebuilds the mechanism stratification; mapping is explicit here
│
├── prompts/                              # the ten conditions as individual text files
│   ├── system_message.txt                # category-neutral system message (placeholder CWE-XX)
│   ├── variant_A_baseline_clean.txt      # and _hinted.txt
│   ├── variant_B_persona_clean.txt       # and _hinted.txt
│   ├── variant_C_patterns_clean.txt      # and _hinted.txt
│   ├── variant_D_cot_clean.txt           # and _hinted.txt
│   └── variant_E_full_clean.txt          # and _hinted.txt
│
└── figures/
    ├── make_figures.py                   # regenerates the three figures (600 dpi PNG)
    ├── make_drawio.py                    # regenerates the editable draw.io figure sources
    ├── Figure1_capability_threshold.{drawio,png}
    ├── Figure2_component_attribution.{drawio,png}
    └── Figure3_sanitisation_mechanism.{drawio,png}

Figure file names follow the numbering used in the paper. The functions inside
make_drawio.py do not: figure2() writes Figure3_*, and figure3() writes
Figure2_*. The two disagreed silently in an earlier revision and a corrected
odds ratio survived in one figure as a result, so the output names are now
aligned to the paper and the mismatch is noted in the source.
```

## 4. Prompt definitions

The ten conditions are provided both as individual text files under `prompts/`
and, canonically, in `vulnbench.py`:

- `SYSTEM_MESSAGE` — the category-neutral system message (uses the placeholder
  `CWE-XX`; no concrete CWE identifier appears in any condition).
- `VARIANTS` — the five structural variants (A–E), composed from the reusable
  task, persona, taint-analysis and chain-of-thought fragments.
- `build_prompt(variant, hint, cwe)` — assembles one condition. CLEAN and
  HINTED forms are strict minimal pairs: HINTED is CLEAN with a single,
  identical category-naming clause inserted at a fixed position, and nothing
  else changed.

These definitions correspond verbatim to Appendix A of the paper.

## 5. Reproducing the results

The notebooks were written for a Google Colab environment and reference paths under Google Drive (a WORK directory holding vulnbench.py and the CSV outputs); these are the execution paths, not the repository layout. To reproduce, adjust ROOT and WORK to your environment; the data files this repository stores under data/ correspond to the CSV outputs the notebooks read and write.

The experiments were run in Google Colab with the corpus on Google Drive. To
reproduce:

1. Place the SARD PHP corpus at the dataset root and `vulnbench.py` alongside
   the benchmark metadata. The notebooks expect a Google Drive layout; adjust
   `ROOT` and `WORK` to your environment.
2. Provide an OpenAI API key when prompted.
3. Run the notebooks in order:
   - `01` verifies benchmark integrity and label correctness (no API calls, free).
   - `02` runs the GPT-4o-mini factorial (~US$0.22).
   - `03` runs GPT-3.5-turbo (~US$0.65) and the first two GPT-5.5 conditions (~US$11).
   - `04` adds the two extra GPT-5.5 runs and merges the three-run stability set (~US$2.7).
   - `05` completes the remaining eight GPT-5.5 conditions and runs the drift
     check (~US$44). It appends to `frontier_gpt55.csv`, backs the file up
     first, and reports which conditions are still missing before it spends
     anything.
   - `06` computes every statistic reported in the paper from the completed
     files (no API calls, free).

Each call is written incrementally, so an interrupted session resumes exactly
where it stopped. Model snapshots are fixed (`gpt-4o-mini`,
`gpt-3.5-turbo-0125`, `gpt-5.5-2026-04-23`); GPT-5.5 is queried at its default
temperature (the API rejects a custom value), and the other two models at
temperature 0.1. Language-model outputs are nondeterministic even at low
temperature, so exact per-call reproduction is not expected; notebook 04
quantifies this (roughly one prediction in ten varies across runs), and the
reported effects are large relative to that variance.

## 6. Execution in stages, and the drift check

The ten GPT-5.5 conditions were not run in one session. The Baseline and Full
Framework conditions under neutral phrasing were run first (notebook 03); the
three remaining neutral conditions and then the five category-naming conditions
were added later (notebook 05), after review made the incomplete factorial a
problem.

Because conditions from different sessions are compared in the same tables, the
Baseline condition was replicated on a stratified 48-sample subset after the
final session, recorded as `run_id = 2` in `drift_check_A_clean.csv`. Verdicts
agreed with the original run on 44 of 48 samples (91.7%). That figure falls
inside the range of within-session agreement measured in notebook 04 (89.6% to
95.8%, mean 93.1%), so the disagreement is attributable to the nondeterminism of
the model rather than to drift between sessions.

## 7. A note on the mechanism stratification

`TABLE4_gpt55_by_sanitizer_mechanism.csv` groups the safe samples by the kind of
sanitisation applied. The mapping from the SARD sanitiser identifier to a
mechanism category is a judgement, and it is now written explicitly in
`scripts/build_table4_mechanism.py` rather than being applied ad hoc, so that it
can be inspected and changed.

Two decisions in that mapping are worth stating. The two samples carrying no
sanitiser at all are labelled `No sanitiser` rather than left empty; the earlier
table left them as a missing value, which `pandas` rendered as `nan` in a
published figure. And `escapeshellarg` is assigned to quote escaping, on the
reading that it escapes metacharacters for a shell sink as the other members of
that group escape for their own sinks; the earlier table left it unassigned.
Including these four samples moves the escaping rate under the Baseline from
21.2% to 20.4% and the odds ratio from 61.5 to 61.3, since all four are
misclassified under either prompt and only the denominator changes.

## 8. Licence

- **Code** (`vulnbench.py`, the notebooks, the scripts under `scripts/`,
  `make_figures.py`, `make_drawio.py`): MIT License.
- **Data, prompts and result files** (benchmark metadata, file list, CSV
  outputs, analysis tables, figure sources): CC BY 4.0.

See `LICENSE` for full text.

## 9. Citation

If you use this package, please cite the paper and the archived release; see
`CITATION.cff`.
