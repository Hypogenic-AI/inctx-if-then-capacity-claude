# Cloned Repositories

## Repo 1: IFEval Official
- **URL**: https://github.com/google-research/google-research/tree/master/instruction_following_eval
- **Purpose**: Official evaluation code for the IFEval benchmark (25 verifiable instruction types)
- **Location**: `code/ifeval_official/`
- **Key files**:
  - `evaluation_main.py` — Main evaluation script
  - `instructions.py` — Instruction definitions and verification functions
  - `instructions_registry.py` — Registry of all 25 instruction types
  - `evaluation_lib.py` — Core evaluation logic
  - `data/` — IFEval prompts data
- **Notes**: Contains deterministic verification functions for each of the 25 instruction types. These can be extended to create verifiers for conditional instructions.

## Repo 2: SIFo Benchmark
- **URL**: https://github.com/shin-ee-chen/SIFo
- **Purpose**: Sequential instruction following benchmark with 4 task types including security rules (conditional)
- **Location**: `code/sifo/`
- **Key files**:
  - `evaluate.py` — Evaluation script
  - `metrics.py` — Evaluation metrics
  - `sifo_datasets/` — Benchmark datasets for all 4 tasks
  - `llm_inference/` — Inference scripts for various LLMs
- **Notes**: The security rules task is the closest existing benchmark to our conditional IF research. Contains both the data and evaluation code.

## Repo 3: FollowBench
- **URL**: https://github.com/YJiangcm/FollowBench
- **Purpose**: Multi-level fine-grained constraints following benchmark
- **Location**: `code/followbench/`
- **Key files**:
  - `data/` — Benchmark data with constraint-evolution paths
  - `code/` — Evaluation code
  - `aggregator.py` — Results aggregation
- **Notes**: Multi-level constraint escalation methodology useful for designing our conditional instruction difficulty levels.

## Repo 4: CoDI-Eval
- **URL**: https://github.com/Xt-cyh/CoDI-Eval
- **Purpose**: Benchmarking controllable generation under diversified instructions
- **Location**: `code/codi-eval/`
- **Key files**:
  - `evaluate.py` — Evaluation script
  - `data/` — Benchmark data
  - `generate.py` — Generation scripts
- **Notes**: Useful for understanding how to diversify constraint expression forms.

## Usage for Experiment Runner

For the "In-context If-Then Capacity" experiment:

1. **IFEval's verification functions** (`code/ifeval_official/instructions.py`) can be adapted to verify conditional instruction outcomes
2. **SIFo's security rules data** (`code/sifo/sifo_datasets/`) provides ready-made conditional instruction test cases
3. **FollowBench's multi-level approach** can inform how to design escalating conditional complexity
4. **CoDI-Eval's diversification pipeline** helps ensure diverse conditional instruction expressions
