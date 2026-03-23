# In-Context If-Then Capacity: Measuring LLM Conditional Instruction Following

## 1. Executive Summary

We systematically measured how well LLMs follow conditional (if-then) instructions across 8 different instruction types. Testing GPT-4.1 and GPT-4o-mini on 120 custom test cases each, we found that **if-then capacity is significantly inconsistent across instruction types**: GPT-4.1 achieved 100% on keyword/format/negation types but only 75% on nested conditionals; GPT-4o-mini ranged from 100% (keyword) to 50% (length). Critically, **the difficulty ranking of instruction types is highly correlated across models** (Spearman ρ=0.83, p=0.011), suggesting that certain conditional instruction types are inherently harder rather than model-specific weaknesses. Error analysis reveals distinct failure modes: GPT-4.1 primarily produces false positives (over-triggering), while GPT-4o-mini primarily produces false negatives (missing triggers), especially for length and nested conditions.

## 2. Goal

**Hypothesis**: The ability of LLMs to follow conditional (if-then) instructions in context is inconsistent across different types of instructions, and this capacity can be systematically measured.

**Why this matters**: LLMs are increasingly deployed with system prompts containing conditional rules (e.g., "if the user asks about X, respond in format Y"). When these rules misfire—triggering when they shouldn't or failing to trigger when they should—it undermines reliability. Understanding which types of conditional instructions are unreliable helps practitioners design more robust prompts.

**Gap filled**: While extensive benchmarks exist for imperative instruction following (IFEval, FollowBench), no dedicated benchmark exists for conditional (if-then) instructions. This work creates the first systematic evaluation of conditional instruction types.

## 3. Data Construction

### Dataset Description
We constructed a custom benchmark of **120 test cases** spanning 8 conditional instruction types. Each instruction type has 2-3 instruction templates, and each template has 3 trigger inputs (condition should activate) and 3 non-trigger inputs (condition should not activate). All conditions and actions are **deterministically verifiable**.

Additionally, we created a **scaling benchmark** of 23 test cases measuring performance with 1, 2, and 4 simultaneous conditional instructions.

### Instruction Types

| Type | Description | Example | # Cases |
|------|-------------|---------|---------|
| keyword | If input contains keyword X, modify output | "If 'urgent' appears, start with PRIORITY:" | 18 |
| format | If input is about topic X, use format Y | "If about a person, respond in JSON" | 18 |
| content | If input mentions X, include Y in response | "If a color is mentioned, include hex code" | 18 |
| length | If input has property X, control response length | "If single word, answer in one sentence" | 12 |
| negation | If input does NOT have X, do Y | "If no question mark, respond in uppercase" | 18 |
| nested | If A, then: if B, do X; else do Y | "If beverage: if hot, 'Enjoy warm!'; if cold, 'Best chilled!'" | 12 |
| multi_and | If both A AND B, then do X | "If both '?' and 'why', start with 'Great question!'" | 12 |
| multi_or | If either A OR B, then do X | "If 'help' or 'assist', start with 'I'm here to help!'" | 12 |

### Example Test Case

**Instruction**: "If the user's message contains the word 'urgent', start your response with 'PRIORITY: ' (exactly). Otherwise, just answer normally."

**Trigger input**: "This is an urgent matter regarding the budget deadline."
→ Expected: Response starts with "PRIORITY: "

**Non-trigger input**: "Can you explain how photosynthesis works?"
→ Expected: Response does NOT start with "PRIORITY: "

### Data Quality
- All 120 test cases have unambiguous trigger/non-trigger designations
- Verification functions are deterministic with tolerance for minor formatting variations
- Each instruction type balanced 50/50 between trigger and non-trigger inputs

## 4. Experiment Description

### Methodology

#### High-Level Approach
We prompt LLMs with a system message containing one conditional instruction, then provide a user message that either triggers or doesn't trigger the condition. We verify compliance using deterministic checker functions (inspired by IFEval's verifiable instruction paradigm).

#### Why This Method?
- **Verifiable conditions**: Unlike subjective instruction quality, our conditions have objectively correct answers
- **Balanced design**: Equal trigger/non-trigger inputs isolate false positive vs false negative errors
- **Diverse types**: 8 types cover different cognitive demands (keyword matching, format switching, logical reasoning, negation)

### Implementation Details

#### Tools and Libraries
- Python 3.12, OpenAI API (v1.x)
- NumPy 2.2.x, SciPy, Pandas, Matplotlib, Seaborn

#### Models
| Model | Provider | Notes |
|-------|----------|-------|
| GPT-4.1 | OpenAI | State-of-the-art instruction follower |
| GPT-4o-mini | OpenAI | Smaller, faster model for comparison |

#### Hyperparameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Temperature | 0.0 | Deterministic for reproducibility |
| Max tokens | 500 | Sufficient for all response types |
| Seed | 42 | API-level seed for reproducibility |

#### Evaluation Protocol
- Each model receives all 120 main benchmark cases + 23 scaling cases
- System prompt contains the conditional instruction
- User message is the test input
- Response verified by type-specific deterministic checker

### Raw Results

#### Main Benchmark: Overall Accuracy

| Model | Accuracy | 95% CI |
|-------|----------|--------|
| GPT-4.1 | **94.2%** | [88.4%, 97.1%] |
| GPT-4o-mini | **82.5%** | [74.7%, 88.3%] |

#### Accuracy by Instruction Type

| Type | GPT-4.1 | GPT-4o-mini |
|------|---------|-------------|
| keyword | **100.0%** | **100.0%** |
| format | **100.0%** | 88.9% |
| multi_or | **100.0%** | 91.7% |
| negation | **100.0%** | 94.4% |
| multi_and | 91.7% | 83.3% |
| length | 91.7% | **50.0%** |
| content | 88.9% | 77.8% |
| nested | **75.0%** | **58.3%** |

#### Error Rates (False Positives and False Negatives)

**GPT-4.1:**

| Type | FPR | FNR | TPR | TNR |
|------|-----|-----|-----|-----|
| keyword | 0.0% | 0.0% | 100% | 100% |
| format | 0.0% | 0.0% | 100% | 100% |
| negation | 0.0% | 0.0% | 100% | 100% |
| multi_or | 0.0% | 0.0% | 100% | 100% |
| length | 0.0% | 16.7% | 83.3% | 100% |
| multi_and | 16.7% | 0.0% | 100% | 83.3% |
| content | **22.2%** | 0.0% | 100% | 77.8% |
| nested | **33.3%** | 16.7% | 83.3% | 66.7% |

**GPT-4o-mini:**

| Type | FPR | FNR | TPR | TNR |
|------|-----|-----|-----|-----|
| keyword | 0.0% | 0.0% | 100% | 100% |
| negation | 0.0% | 11.1% | 88.9% | 100% |
| length | 0.0% | **100%** | 0.0% | 100% |
| format | 11.1% | 11.1% | 88.9% | 88.9% |
| multi_or | 16.7% | 0.0% | 100% | 83.3% |
| multi_and | 16.7% | 16.7% | 83.3% | 83.3% |
| content | 22.2% | 22.2% | 77.8% | 77.8% |
| nested | **50.0%** | 33.3% | 66.7% | 50.0% |

#### Scaling Benchmark

| Model | 1 condition | 2 conditions | 4 conditions |
|-------|-------------|--------------|--------------|
| GPT-4.1 | 100% | 91.7% | 100% |
| GPT-4o-mini | 100% | 100% | 100% |

Per-marker accuracy (individual condition compliance within multi-condition prompts):
- GPT-4.1: 95.8% (2 conds), 100% (4 conds)
- GPT-4o-mini: 100% (2 conds), 100% (4 conds)

## 5. Result Analysis

### Key Findings

**Finding 1: If-then capacity varies dramatically by instruction type.**
- GPT-4.1: 25 percentage point range (75%-100%) across types
- GPT-4o-mini: 50 percentage point range (50%-100%) across types
- For GPT-4o-mini, this variation is statistically significant: χ²=20.72, df=7, p=0.004, Cramér's V=0.42 (medium-large effect)
- For GPT-4.1, the variation approaches significance: χ²=13.30, df=7, p=0.065, Cramér's V=0.33

**Finding 2: Difficulty ranking is consistent across models.**
- Spearman rank correlation ρ=0.83, p=0.011
- Both models find nested conditionals hardest and keyword conditionals easiest
- This suggests instruction type difficulty is an inherent property of the task, not a model-specific weakness

**Finding 3: Error modes differ by model capability.**
- GPT-4.1 predominantly makes **false positive errors** (over-triggering): it tends to perform the conditional action even when the condition isn't met. This is especially notable for content-type instructions (22.2% FPR) and nested conditionals (33.3% FPR).
- GPT-4o-mini predominantly makes **false negative errors** (under-triggering): it misses conditions that should fire. Most dramatically, it completely fails length-conditional instructions (100% FNR—never correctly shortens/lengthens response based on input properties).

**Finding 4: Difficulty hierarchy of conditional types.**
From easiest to hardest (averaged across models):
1. **Keyword** (100%): Simple string-matching conditions are trivially easy
2. **Negation** (97.2%): "If NOT X" is surprisingly well-handled
3. **Multi-OR** (95.8%): Disjunctive conditions are near-perfect
4. **Format** (94.4%): Format-switching on topic detection works well
5. **Multi-AND** (87.5%): Conjunctive conditions show some degradation
6. **Content** (83.3%): Semantic content detection is harder than keyword matching
7. **Length** (70.8%): Length control based on input properties is unreliable
8. **Nested** (66.7%): Multi-level conditional branching is the hardest

**Finding 5: Scaling with simple marker-based conditions works well.**
Both models maintained near-perfect accuracy even with 4 simultaneous conditions when the conditions were simple keyword→marker mappings. This suggests the capacity bottleneck is in the *complexity* of individual conditions, not the *number* of conditions (at least up to 4).

### Qualitative Error Analysis

**False Positive Pattern (GPT-4.1 "over-triggering")**:
- The "content" type produced the most false positives. When asked about plants and instructed to include a hex color code only if a color is mentioned, GPT-4.1 included `#228B22` (forest green) because it associated "plants" with the color green. This is semantic over-generalization—the model interprets the condition too broadly.
- Similarly, "I visited the aquarium today" (no animal explicitly mentioned) triggered the "Fun animal fact:" suffix because the model associated aquariums with animals.

**False Negative Pattern (GPT-4o-mini)**:
- Length-conditional instructions completely failed: when told "if single word input, respond in one sentence", GPT-4o-mini always produced multi-sentence responses regardless of input length. The model doesn't seem to attend to meta-properties of the input (like word count) when those are specified as conditions.
- This is a *capability gap*, not a stochastic failure—it was 100% consistent in failing.

**Nested Conditional Failures (both models)**:
- The paragraph-count-based nested condition (even number → 2 paragraphs, odd → 3) was hardest. Models produced 2 paragraphs as a "default" behavior regardless of the condition, suggesting they treat paragraph structure as a formatting preference rather than a precisely controllable parameter.

### Hypothesis Testing Results

| Hypothesis | Result | Evidence |
|-----------|--------|----------|
| H1: >15% accuracy range across types | **Supported** | GPT-4.1: 25% range; GPT-4o-mini: 50% range |
| H2: FNR and FPR vary by type differently | **Supported** | GPT-4.1 skews FP; GPT-4o-mini skews FN. Both vary dramatically by type. |
| H3: Degradation with more conditions | **Not supported** (for simple conditions) | Near-perfect at 1-4 simple conditions. Complexity, not count, drives failure. |
| H4: Consistent difficulty ranking across models | **Supported** | ρ=0.83, p=0.011 |

### Visualizations

Key plots saved in `results/plots/`:
- `accuracy_by_type.png`: Bar chart comparing both models across 8 types
- `fpr_fnr_gpt-4_1.png` and `fpr_fnr_gpt-4o-mini.png`: Error type breakdown
- `trigger_vs_nontrigger.png`: TPR vs TNR per type
- `scaling_curve.png`: Accuracy vs number of conditions
- `cross_model_scatter.png`: Type difficulty correlation between models
- `radar_*.png`: Capacity profile radar charts

### Limitations

1. **Sample size**: 120 cases per model (12-18 per type) provides moderate statistical power. Larger samples would yield tighter confidence intervals.
2. **Two models only**: Testing GPT-4.1 and GPT-4o-mini from the same family limits generalizability. Claude, Gemini, and open-source models should be tested.
3. **Simple conditions**: Our conditions are relatively clean and unambiguous. Real-world conditional instructions are often more vague.
4. **Verifier tolerance**: Some verifiers use heuristics (e.g., sentence counting, paragraph splitting) that may introduce measurement noise.
5. **Single run**: Temperature=0 gives deterministic results, but doesn't capture variance under stochastic sampling.
6. **Scaling benchmark used simple conditions**: The marker-based scaling test may underestimate degradation with complex conditions composed together.

## 6. Conclusions

### Summary
LLM conditional instruction-following capacity is **significantly inconsistent across instruction types**, with accuracy ranging from 100% (keyword matching) to 50% (length control) depending on the type. The difficulty ranking is consistent across models (ρ=0.83), establishing a **hierarchy of conditional instruction difficulty**: keyword < negation < multi-OR < format < multi-AND < content < length < nested. The capacity bottleneck is in individual condition complexity, not the number of simultaneous conditions.

### Implications

**For practitioners**:
- Prefer keyword-based conditions over semantic or length-based conditions in system prompts
- Avoid nested if-then-else logic; flatten into separate rules
- Test conditional instructions with both trigger and non-trigger inputs before deployment
- Be aware that stronger models (GPT-4.1) tend to over-trigger, while weaker models tend to miss triggers

**For researchers**:
- Conditional instruction following is a distinct capability from imperative instruction following
- A dedicated benchmark (like ours) is needed to evaluate this capability
- The false positive vs false negative asymmetry provides insight into how models process conditions internally

### Confidence in Findings
**Moderate-high**. The core finding (inconsistency across types) is robust: it's statistically significant for GPT-4o-mini and the ranking correlation is strong. The specific accuracy numbers should be treated as estimates given sample sizes.

## 7. Next Steps

### Immediate Follow-ups
1. **Expand to more models**: Test Claude, Gemini, Llama-3, and Qwen to validate cross-model consistency
2. **Increase sample size**: 50+ cases per type for tighter confidence intervals
3. **Complex scaling**: Combine *different types* of conditions (not just keyword→marker) to test true multi-condition capacity
4. **Natural language variation**: Test the same logical condition expressed in different phrasings

### Alternative Approaches
- **Prompt engineering**: Test whether chain-of-thought or pseudo-code formatting improves conditional compliance
- **Fine-tuning**: Targeted training on conditional instructions
- **Mechanistic analysis**: Probe model internals for conditional instruction processing signals (extending Heo et al. 2024)

### Open Questions
- Does the difficulty hierarchy hold for generative tasks beyond simple compliance checking?
- Can models learn to be more reliable on hard types (nested, length) through in-context examples?
- Is the false-positive asymmetry in stronger models a fundamental trade-off between precision and recall in instruction following?

## References

1. Zhou et al. (2023). IFEval: Instruction-Following Evaluation for Large Language Models. arXiv:2311.07911
2. Chen et al. (2024). The SIFo Benchmark: Sequential Instruction Following. arXiv:2406.19999
3. Jiang et al. (2023). FollowBench: Multi-level Fine-grained Constraints Following. arXiv:2310.07641
4. Yao et al. (2023). COLLIE: Systematic Construction of Constrained Text Generation Tasks. arXiv:2307.06439
5. Heo et al. (2024). Do LLMs "know" internally when they follow instructions? arXiv:2410.14516
6. Kumar et al. (2025). Training with Pseudo-Code for Instruction Following.
7. Wu et al. (2025). When Thinking Fails: Pitfalls of Reasoning for Instruction-Following.
