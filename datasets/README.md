# Downloaded Datasets

This directory contains datasets for the "In-context If-Then Capacity" research project. Data files are NOT committed to git due to size. Follow the download instructions below.

## Dataset 1: IFEval (Google)

### Overview
- **Source**: `google/IFEval` on HuggingFace
- **Size**: 541 prompts
- **Format**: HuggingFace Dataset
- **Task**: Verifiable instruction following with 25 constraint types
- **Splits**: train (541)
- **License**: Apache 2.0

### Download Instructions

```python
from datasets import load_dataset
dataset = load_dataset("google/IFEval")
dataset.save_to_disk("datasets/ifeval")
```

### Loading the Dataset

```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/ifeval")
```

### Fields
- `key`: Unique identifier
- `prompt`: The instruction prompt with verifiable constraints
- `instruction_id_list`: List of constraint type IDs (e.g., "punctuation:no_comma")
- `kwargs`: Parameters for each constraint (e.g., keyword lists, word counts)

### Notes
- Each prompt contains 1-3 verifiable instructions
- 25 constraint types across 7 groups (Keywords, Language, Length, Content, Format, Cases, Punctuation)
- Evaluation code available in `code/ifeval_official/`

---

## Dataset 2: InFoBench

### Overview
- **Source**: `kqsong/InFoBench` on HuggingFace
- **Size**: 500 prompts
- **Format**: HuggingFace Dataset
- **Task**: Decomposed instruction evaluation with fine-grained questions
- **Splits**: train (500)

### Download Instructions

```python
from datasets import load_dataset
dataset = load_dataset("kqsong/InFoBench")
dataset.save_to_disk("datasets/infobench")
```

### Loading the Dataset

```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/infobench")
```

### Fields
- `id`: Unique identifier
- `input`: Context/background information
- `category`: Task category (e.g., Quora, ShareGPT)
- `instruction`: The instruction to follow
- `decomposed_questions`: Fine-grained evaluation questions
- `subset`: Data subset
- `question_label`: Labels for decomposed questions

---

## Dataset 3: BIG-Bench Hard (BBH) — Logical Reasoning Subtasks

### Overview
- **Source**: `lukaemon/bbh` on HuggingFace
- **Size**: 187-250 test samples per task
- **Format**: HuggingFace Dataset
- **Tasks downloaded**:
  - `navigate` (250 samples) — spatial reasoning with conditional steps
  - `logical_deduction_three_objects` (250 samples) — logical constraint satisfaction
  - `boolean_expressions` (250 samples) — evaluating boolean logic
  - `causal_judgement` (187 samples) — causal/conditional reasoning

### Download Instructions

```python
from datasets import load_dataset
for task in ["navigate", "logical_deduction_three_objects", "boolean_expressions", "causal_judgement"]:
    ds = load_dataset("lukaemon/bbh", task)
    ds.save_to_disk(f"datasets/bbh/{task}")
```

### Fields
- `input`: The reasoning problem
- `target`: The correct answer

---

## Notes for Experiment Runner

For our "In-context If-Then Capacity" research, these datasets serve different purposes:

1. **IFEval**: Baseline for verifiable instruction following — extend its paradigm to conditional instructions
2. **InFoBench**: Decomposed evaluation approach — useful for analyzing which sub-conditions fail
3. **BBH logical tasks**: Test pure conditional/logical reasoning ability as a baseline

A **custom dataset will need to be constructed** for the core experiment: if-then conditional instructions where both trigger conditions and required actions are verifiable. See `literature_review.md` for detailed design recommendations.
