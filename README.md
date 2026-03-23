# In-Context If-Then Capacity

Measuring how consistently LLMs follow conditional (if-then) instructions across different instruction types.

## Key Findings

- **If-then capacity varies dramatically by instruction type**: 25-50 percentage point accuracy range across 8 types
- **Difficulty hierarchy**: keyword (100%) > negation (97%) > multi-OR (96%) > format (94%) > multi-AND (88%) > content (83%) > length (71%) > nested (67%)
- **Consistent across models**: Type difficulty ranking correlates strongly between GPT-4.1 and GPT-4o-mini (Spearman ρ=0.83, p=0.011)
- **Different error modes**: Stronger models over-trigger (false positives); weaker models miss triggers (false negatives)
- **Condition count ≠ bottleneck**: Models handle 4 simultaneous simple conditions perfectly; complexity of individual conditions drives failure

## Quick Start

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install openai numpy scipy matplotlib seaborn pandas

# Run experiments (requires OPENAI_API_KEY)
python src/run_experiment.py

# Analyze results
python src/analyze.py
```

## Project Structure

```
├── REPORT.md              # Full research report with all results
├── planning.md            # Research plan and methodology
├── src/
│   ├── benchmark.py       # Benchmark construction (8 types, 120 cases)
│   ├── verifiers.py       # Deterministic verification functions
│   ├── run_experiment.py   # API experiment runner
│   └── analyze.py         # Statistical analysis and visualization
├── results/
│   ├── main_results.json   # Raw model outputs + verification
│   ├── scaling_results.json
│   ├── summary.json        # Aggregated statistics
│   ├── config.json         # Experiment configuration
│   └── plots/              # All visualizations
├── literature_review.md    # Survey of related work
├── resources.md            # Catalog of gathered resources
├── papers/                 # Downloaded research papers
├── datasets/               # Pre-downloaded datasets (IFEval, BBH, etc.)
└── code/                   # Cloned baseline repositories
```

See [REPORT.md](REPORT.md) for the full research report.
