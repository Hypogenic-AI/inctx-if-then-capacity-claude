# Literature Review: In-context If-Then Capacity of Large Language Models

## Research Area Overview

This review surveys the ability of large language models (LLMs) to follow conditional (if-then) instructions provided in context. The research hypothesis is that LLMs' capacity to follow such conditional instructions is inconsistent across different instruction types. This sits at the intersection of instruction following evaluation, constrained text generation, and logical reasoning in LLMs.

The field has rapidly evolved from basic instruction-following benchmarks to sophisticated multi-constraint and sequential evaluation frameworks. Key themes include: (1) verifiable instruction evaluation, (2) multi-constraint and compositional instruction following, (3) sequential/conditional instruction dependencies, and (4) internal mechanisms for instruction adherence.

## Key Papers

### 1. IFEval: Instruction-Following Evaluation for Large Language Models
- **Authors**: Zhou et al.
- **Year**: 2023
- **Source**: arXiv:2311.07911
- **Key Contribution**: Introduced the concept of "verifiable instructions" — instructions that can be objectively and automatically verified. Defined 25 types of verifiable instructions across 7 groups: Keywords, Language, Length Constraints, Detectable Content, Detectable Format, Change Cases, Start/End with, Punctuation.
- **Methodology**: 541 prompts with one or more verifiable instructions per prompt. Deterministic verification functions check compliance.
- **Datasets Used**: Custom-built 541 prompts
- **Results**: GPT-4 outperforms PaLM 2; models struggle more with compositional constraints (multiple instructions per prompt).
- **Code Available**: Yes — https://github.com/google-research/google-research/tree/master/instruction_following_eval
- **Relevance**: Foundational benchmark. Provides the evaluation paradigm (verifiable constraints) that we can extend to conditional (if-then) instructions.

### 2. The SIFo Benchmark: Sequential Instruction Following
- **Authors**: Chen, Liao, Qi, Eustratiadis, Monz, Bisazza, de Rijke
- **Year**: 2024
- **Source**: arXiv:2406.19999
- **Key Contribution**: First benchmark for *sequential* instruction following where success of each step depends on the previous step. Addresses coherence between instructions, positional bias, and objective verifiability.
- **Methodology**: Four task types: text modification, question answering, mathematics, and security rules. The security rules task is particularly relevant — it requires following conditional rules (e.g., correct password → allow action; wrong password → deny action).
- **Results**: All models struggle with later steps in sequences. Even GPT-4 performance degrades significantly on longer instruction chains. Larger/newer models outperform smaller/older ones.
- **Code Available**: Yes — https://github.com/shin-ee-chen/SIFo
- **Relevance**: **Highly relevant**. The security rules task is a direct instance of conditional (if-then) instruction following. The sequential nature tests cumulative conditional reasoning.

### 3. FollowBench: Multi-level Fine-grained Constraints Following
- **Authors**: Jiang et al.
- **Year**: 2023
- **Source**: arXiv:2310.07641 (FollowBench paper)
- **Key Contribution**: Proposes a multi-level mechanism that incrementally adds constraints, with five constraint types: Content, Situation, Style, Format, and Example. Uses constraint-evolution paths for evaluation.
- **Methodology**: 13 LLMs evaluated with incrementally harder constraint levels.
- **Code Available**: Yes — https://github.com/YJiangcm/FollowBench
- **Relevance**: The multi-level constraint escalation is relevant for studying how conditional capacity degrades as constraint complexity increases.

### 4. COLLIE: Systematic Construction of Constrained Text Generation Tasks
- **Authors**: Yao, Chen, Hanjie, Yang, Narasimhan
- **Year**: 2023
- **Source**: arXiv:2307.06439
- **Key Contribution**: Grammar-based framework for specifying rich, compositional constraints at multiple generation levels (word, sentence, paragraph, passage). Includes 13 constraint structures in COLLIE-v1.
- **Methodology**: Compositional constraint specification and automatic evaluation.
- **Relevance**: Provides a systematic framework for constructing diverse constraint types, including conditional constraints.

### 5. Benchmarking Complex Instruction-Following with Multiple Constraints Composition
- **Authors**: Qin et al.
- **Year**: 2024
- **Key Contribution**: Studies how LLMs handle compositions of multiple constraints simultaneously, finding that performance degrades with increasing constraint count.
- **Relevance**: Directly relevant to understanding capacity limits for conditional instructions composed with other constraints.

### 6. Do LLMs "know" internally when they follow instructions?
- **Authors**: Heo et al.
- **Year**: 2024
- **Key Contribution**: Discovers an "instruction-following dimension" in LLM embedding space that predicts compliance. This dimension generalizes across tasks but NOT across instruction types.
- **Relevance**: **Highly relevant**. The finding that the instruction-following dimension does not generalize across instruction types supports our hypothesis that if-then capacity varies by instruction type.

### 7. CoDI-Eval: Benchmarking LLMs on Controllable Generation under Diversified Instructions
- **Authors**: Chen et al.
- **Year**: 2024
- **Key Contribution**: Evaluates controllability under diversified constraint expressions and fine-grained sub-categories. Shows significant gap between open-source and closed-source LLMs.
- **Code Available**: Yes — https://github.com/Xt-cyh/CoDI-Eval
- **Relevance**: Provides methodology for diversifying constraint expressions, applicable to conditional instructions.

### 8. When Thinking Fails: Pitfalls of Reasoning for Instruction-Following
- **Authors**: Wu et al.
- **Year**: 2025
- **Key Contribution**: Shows that reasoning models (chain-of-thought) can actually hurt instruction-following performance in some cases, particularly for constraint adherence.
- **Relevance**: Important for understanding whether CoT helps or hurts conditional instruction following.

### 9. Training with Pseudo-Code for Instruction Following
- **Authors**: Kumar, Murthy, Bhat, Contractor
- **Year**: 2025
- **Key Contribution**: Shows that expressing instructions as pseudo-code improves following, especially for compositional structures. 8-21% gains on IF benchmarks.
- **Relevance**: Pseudo-code naturally captures if-then logic, suggesting conditional instructions may benefit from structured representations.

### 10. Only-IF: Revealing the Decisive Effect of Instruction Diversity on Generalization
- **Authors**: Zhang, Wang, Charton
- **Year**: 2024
- **Key Contribution**: Demonstrates that generalization to unseen instructions ONLY emerges when training data is diverse enough across semantic domains. Cross-domain diversity matters more than within-domain quantity.
- **Relevance**: Suggests that if-then capacity may depend on exposure to diverse conditional instruction types during training.

## Common Methodologies

1. **Verifiable Constraint Evaluation** (IFEval, SIFo, FollowBench): Define constraints with deterministic verification functions
2. **Multi-level Difficulty Scaling** (FollowBench, COLLIE): Incrementally add constraints to measure capacity limits
3. **Sequential Dependency Chains** (SIFo): Chain instructions where each depends on the previous
4. **Activation/Representation Analysis** (Heo et al., activation steering): Probe internal model states for instruction-following signals
5. **Compositional Constraint Synthesis** (COLLIE, CoDI-Eval): Systematically compose constraint types

## Standard Baselines

- **GPT-4/GPT-4o**: Strongest closed-source baseline across all benchmarks
- **Claude-3**: Strong on sequential tasks (SIFo)
- **Llama-3 (8B, 70B)**: Standard open-source baselines
- **Qwen2 (7B, 72B)**: Strong open-source alternative
- **Mistral-7B**: Compact baseline

## Evaluation Metrics

- **Prompt-level accuracy**: Whether ALL constraints in a prompt are satisfied (strict)
- **Instruction-level accuracy**: Fraction of individual constraints satisfied (loose)
- **Step-wise accuracy**: Performance at each step in a sequence (SIFo)
- **Constraint satisfaction rate (CSR)**: Per-constraint-type success rate
- **Level-wise performance**: Accuracy at each difficulty level (FollowBench)

## Datasets in the Literature

| Dataset | Used In | Task | Size |
|---------|---------|------|------|
| IFEval | Zhou et al. 2023, many follow-ups | 25 verifiable constraint types | 541 prompts |
| SIFo | Chen et al. 2024 | Sequential IF (4 task types) | ~1000 instances |
| FollowBench | Jiang et al. 2023 | 5 constraint categories, multi-level | ~800 instances |
| COLLIE-v1 | Yao et al. 2023 | 13 constraint structures | 2080 instances |
| CoDI-Eval | Chen et al. 2024 | Diversified constraint expressions | Large |
| InFoBench | Qin et al. 2024 | Decomposed instruction evaluation | 500 prompts |
| BBH | Suzgun et al. 2023 | Logical reasoning subtasks | 250/task |

## Gaps and Opportunities

1. **No dedicated benchmark for conditional (if-then) instructions**: Existing benchmarks focus on imperative constraints ("do X") rather than conditional ones ("if Y, then do X"). SIFo's security rules task is the closest, but it's only one of four task types.

2. **If-then instruction types not systematically categorized**: The literature lacks a taxonomy of conditional instruction types (e.g., input-conditional, context-conditional, output-conditional, nested conditionals, negated conditionals).

3. **Inconsistency across instruction types unexplored for conditionals**: Heo et al. showed that internal instruction-following signals don't generalize across instruction types. This hasn't been specifically studied for conditional instructions.

4. **Interaction between conditional logic and other constraints under-studied**: How do if-then instructions interact with format, length, and content constraints?

5. **No evaluation of conditional instruction capacity scaling**: How does performance change with number of conditions, nesting depth, or logical complexity?

## Recommendations for Our Experiment

Based on the literature review:

- **Recommended datasets**:
  - IFEval (541 prompts) — baseline for verifiable instruction following
  - SIFo (security rules subset) — closest existing benchmark for conditional IF
  - InFoBench (500 prompts) — for decomposed instruction analysis
  - BBH logical tasks — for logical/conditional reasoning baselines
  - **Custom dataset needed**: Design if-then conditional instructions with verifiable outcomes

- **Recommended baselines**: GPT-4o, Claude-3.5 Sonnet, Llama-3-70B, Qwen2-72B, and at least one small model (Llama-3-8B or Mistral-7B)

- **Recommended metrics**:
  - Prompt-level accuracy (strict: all conditions met)
  - Instruction-level accuracy (loose: per-condition)
  - Conditional accuracy by type (condition trigger rate, action compliance rate)
  - Breakdown by: condition type, nesting depth, logical complexity

- **Methodological considerations**:
  - Use IFEval's verifiable instruction paradigm but extend to conditional instructions
  - Design if-then instructions where both the condition and the action are verifiable
  - Test multiple condition types: keyword-based, format-based, content-based, counting-based
  - Include negated conditions ("if NOT X, then Y"), nested conditions, and multi-condition ANDs/ORs
  - Compare structured (pseudo-code) vs. natural language conditional instructions
