# Resources Catalog

## Summary
This document catalogs all resources gathered for the "In-context If-Then Capacity" research project, investigating how consistently LLMs follow conditional (if-then) instructions across different instruction types.

## Papers
Total papers downloaded: 23

| Title | Authors | Year | File | Key Info |
|-------|---------|------|------|----------|
| IFEval | Zhou et al. | 2023 | papers/zhou2023_ifeval.pdf | Foundational verifiable IF benchmark, 25 constraint types |
| SIFo Benchmark | Chen et al. | 2024 | papers/chen2024_sifo.pdf | Sequential IF with security rules (conditional) |
| FollowBench | Jiang et al. | 2023 | papers/jiang2023_followbench.pdf | Multi-level constraint following |
| COLLIE | Yao et al. | 2023 | papers/yao2023_collie.pdf | Compositional constrained generation framework |
| InFoBench | Qin et al. | 2023 | papers/qin2023_infobench.pdf | Decomposed instruction evaluation |
| Chain of Thought | Wei et al. | 2022 | papers/wei2022_cot.pdf | CoT prompting for reasoning |
| Know Internally IF | Heo et al. | 2024 | papers/heo2024_know_internally.pdf | IF dimension in embedding space |
| Complex to Simple | He et al. | 2024 | papers/he2024_complex_to_simple.pdf | Multi-constraint IF enhancement |
| When Thinking Fails | Wu et al. | 2025 | papers/wu2025_thinking_fails.pdf | Reasoning pitfalls for IF |
| DeCRIM | Chen et al. | 2024 | papers/chen2024_decrim.pdf | Self-correction for multi-constraint IF |
| Activation Steering IF | Chen et al. | 2024 | papers/chen2024_activation_steering.pdf | Representation engineering for IF |
| Conifer | Sun et al. | 2024 | papers/sun2024_conifer.pdf | Complex constrained IF |
| Only-IF | Zhang et al. | 2024 | papers/zhang2024_only_if.pdf | Instruction diversity → generalization |
| RuleR | Mu et al. | 2024 | papers/mu2024_ruler.pdf | Rule-based controllability |
| Pseudo-Code IF | Kumar et al. | 2025 | papers/li2024_pseudocode_if.pdf | Structured IF representations |
| VerIF | Peng et al. | 2025 | papers/peng2025_verif.pdf | Verification engineering for IF |
| Scaling Reasoning | Xia et al. | 2025 | papers/xia2025_scaling_reasoning.pdf | IF in reasoning models |
| Multi-Dim Constraint | Sun et al. | 2024 | papers/sun2024_multi_dim.pdf | Constraint pattern framework |
| Spotlight Instructions | Li et al. | 2025 | papers/spotlight2025_dynamic_attention.pdf | Dynamic attention steering |
| Turking Test | Efrat & Levy | 2020 | papers/efrat2020_turking_test.pdf | Early instruction understanding |
| CoDI-Eval | Chen et al. | 2024 | papers/chen2024_codi_eval.pdf | Diversified constraint evaluation |

See `papers/README.md` for detailed descriptions.

## Datasets
Total datasets downloaded: 3 (+ 4 BBH subtasks)

| Name | Source | Size | Task | Location | Notes |
|------|--------|------|------|----------|-------|
| IFEval | google/IFEval | 541 prompts | Verifiable IF | datasets/ifeval/ | Core baseline dataset |
| InFoBench | kqsong/InFoBench | 500 prompts | Decomposed IF | datasets/infobench/ | Fine-grained evaluation |
| BBH Navigate | lukaemon/bbh | 250 samples | Spatial reasoning | datasets/bbh/navigate/ | Conditional reasoning |
| BBH Logical Deduction | lukaemon/bbh | 250 samples | Logic | datasets/bbh/logical_deduction_three_objects/ | Constraint satisfaction |
| BBH Boolean Expressions | lukaemon/bbh | 250 samples | Boolean logic | datasets/bbh/boolean_expressions/ | If-then logic baseline |
| BBH Causal Judgement | lukaemon/bbh | 187 samples | Causal reasoning | datasets/bbh/causal_judgement/ | Conditional reasoning |

See `datasets/README.md` for detailed descriptions and download instructions.

## Code Repositories
Total repositories cloned: 4

| Name | URL | Purpose | Location | Notes |
|------|-----|---------|----------|-------|
| IFEval Official | github.com/google-research/... | Evaluation code + verifiers | code/ifeval_official/ | 25 verifiable instruction types |
| SIFo | github.com/shin-ee-chen/SIFo | Sequential IF benchmark | code/sifo/ | Security rules = conditional IF |
| FollowBench | github.com/YJiangcm/FollowBench | Multi-level constraint following | code/followbench/ | Constraint evolution paths |
| CoDI-Eval | github.com/Xt-cyh/CoDI-Eval | Diversified constraint eval | code/codi-eval/ | Constraint diversification |

See `code/README.md` for detailed descriptions.

## Resource Gathering Notes

### Search Strategy
1. Used paper-finder service with 3 targeted queries (conditional IF, in-context learning rules, IFEval benchmarks)
2. Found 415 unique papers across searches
3. Filtered to 23 most relevant papers based on relevance scores and keyword matching
4. Searched HuggingFace for existing datasets
5. Cloned 4 code repositories with evaluation frameworks

### Selection Criteria
- Papers: Focused on instruction following evaluation, constraint-based generation, conditional/logical reasoning, and mechanism analysis
- Datasets: Prioritized verifiable evaluation datasets with constraint types related to conditional instructions
- Code: Selected repositories with evaluation frameworks that can be adapted for conditional IF evaluation

### Challenges Encountered
- Several arXiv IDs from Semantic Scholar API were incorrect/mismatched (paper content didn't match expected title)
- FollowBench and CoDI-Eval datasets not available on HuggingFace Hub (data is in their GitHub repos)
- FOLIO dataset (logical reasoning) requires gated access
- No existing dataset specifically targets in-context if-then conditional instructions

### Gaps and Workarounds
- **No dedicated if-then IF dataset exists**: Recommend constructing a custom dataset based on IFEval's verifiable instruction paradigm
- **SIFo security rules** are the closest proxy for conditional IF evaluation
- **BBH logical tasks** provide baseline conditional reasoning capability measurements

## Recommendations for Experiment Design

Based on gathered resources, recommend:

1. **Primary dataset(s)**:
   - IFEval for baseline verifiable IF measurement
   - SIFo security rules for existing conditional IF evaluation
   - **Custom if-then dataset** (to be constructed) as the core experiment
   - BBH boolean/logical tasks for reasoning baseline

2. **Baseline methods**:
   - Direct prompting (zero-shot)
   - Chain-of-thought prompting
   - Pseudo-code instruction formatting
   - Compare across model families (GPT-4, Claude, Llama, Qwen)

3. **Evaluation metrics**:
   - Condition detection rate (does the model recognize when a condition is triggered?)
   - Action compliance rate (when condition is met, does the model perform the correct action?)
   - Negation handling (if-not-X behavior)
   - Compositional conditional accuracy (AND/OR conditions)
   - Per-type breakdown across different conditional instruction categories

4. **Code to adapt/reuse**:
   - `code/ifeval_official/instructions.py` — Adapt verification functions for conditional instructions
   - `code/sifo/` — Use security rules task as template for conditional IF evaluation
   - `code/followbench/` — Multi-level difficulty design pattern
   - `code/codi-eval/` — Constraint expression diversification pipeline

5. **Proposed custom dataset design** (if-then conditional instructions):
   - **Type 1: Format-conditional** — "If the topic is about science, respond in JSON format; otherwise, use bullet points"
   - **Type 2: Content-conditional** — "If the user mentions a city, include population data; if they mention a country, include GDP"
   - **Type 3: Keyword-conditional** — "If the word 'urgent' appears, start with 'PRIORITY:'; otherwise, start with 'Note:'"
   - **Type 4: Length-conditional** — "If the question is about history, answer in at least 200 words; if about math, answer concisely"
   - **Type 5: Negation-conditional** — "If the input does NOT contain numbers, respond in all caps"
   - **Type 6: Nested-conditional** — "If A, then: if B, do X; else do Y"
   - **Type 7: Multi-condition (AND)** — "If both keyword1 and keyword2 appear, then..."
   - **Type 8: Multi-condition (OR)** — "If either keyword1 or keyword2 appears, then..."
