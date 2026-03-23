# Research Plan: In-context If-Then Capacity

## Motivation & Novelty Assessment

### Why This Research Matters
LLMs are increasingly used as instruction-following agents where system prompts contain conditional rules (e.g., "if the user asks about X, respond with Y"). When these conditional instructions misfire—either failing to trigger when they should (false negatives) or triggering when they shouldn't (false positives)—it undermines reliability in production deployments. Understanding where and why these failures occur is critical for building trustworthy LLM-based systems.

### Gap in Existing Work
The literature review reveals that while extensive benchmarks exist for imperative instruction following (IFEval, FollowBench, COLLIE), **no dedicated benchmark exists for conditional (if-then) instructions**. SIFo's security rules are the closest proxy but cover only one narrow type. Heo et al. (2024) showed that internal instruction-following signals don't generalize across instruction types, suggesting conditional IF capacity may vary systematically—but this hasn't been tested.

### Our Novel Contribution
We create a systematic benchmark of **8 types of conditional instructions** with verifiable triggers and actions, measure LLM performance across these types, and quantify the **consistency** of if-then capacity. We decompose errors into false positives (action taken when condition not met) vs. false negatives (action not taken when condition met), providing a fine-grained view of conditional instruction failure modes.

### Experiment Justification
- **Experiment 1 (Custom If-Then Benchmark)**: Core contribution—no such benchmark exists. Tests 8 conditional instruction types with both trigger and non-trigger inputs.
- **Experiment 2 (Cross-model comparison)**: Tests whether inconsistency patterns are model-specific or universal, using GPT-4.1 and GPT-4o-mini.
- **Experiment 3 (Scaling analysis)**: Tests how performance changes with number of simultaneous conditional instructions (1, 2, 4 conditions).

## Research Question
How consistently can LLMs follow conditional (if-then) instructions across different instruction types, and can we measure their capacity for such instructions?

## Hypothesis Decomposition
1. **H1**: LLM accuracy on conditional instructions varies significantly across instruction types (>15% range between best and worst type).
2. **H2**: False negatives (missing a triggered condition) and false positives (acting on untriggered condition) occur at different rates, and their relative frequency varies by instruction type.
3. **H3**: Performance degrades as the number of simultaneous conditional instructions increases.
4. **H4**: Error patterns are partially consistent across models (same instruction types are hard for different models).

## Proposed Methodology

### Approach
Create a benchmark of if-then conditional instructions across 8 types. For each type, create instruction-input pairs where:
- Half of inputs **trigger** the condition (should produce conditional action)
- Half of inputs **do not trigger** the condition (should produce default action)

Both the condition trigger and the resulting action are **verifiable** using deterministic checks (following IFEval's paradigm).

### Instruction Types (8 categories)
1. **Keyword-conditional**: "If the input contains the word 'urgent', start your response with 'PRIORITY:'"
2. **Format-conditional**: "If the input asks about a person, respond in JSON format with name/role fields"
3. **Length-conditional**: "If the input is a yes/no question, answer in exactly one sentence"
4. **Content-conditional**: "If the input mentions a number, include a calculation in your response"
5. **Negation-conditional**: "If the input does NOT contain a question mark, respond in all capital letters"
6. **Nested-conditional**: "If the input mentions food: if it's a fruit, list vitamins; if it's a vegetable, list minerals"
7. **Multi-condition AND**: "If the input contains both a color AND an animal, describe the animal in that color"
8. **Multi-condition OR**: "If the input mentions either 'help' OR 'assist', begin with 'I'm here to help:'"

### Experimental Steps
1. Generate 10 instruction templates per type (80 total)
2. For each instruction, create 2 trigger inputs + 2 non-trigger inputs (320 test cases)
3. Add a scaling experiment: combine 1, 2, and 4 conditional instructions per prompt
4. Run through GPT-4.1 and GPT-4o-mini
5. Verify outputs using deterministic checkers
6. Compute metrics per type, per model, per scaling level

### Baselines
- **Random baseline**: Expected ~50% accuracy (chance of matching trigger/non-trigger)
- **Cross-type comparison**: Each instruction type serves as baseline for others

### Evaluation Metrics
- **Overall accuracy**: Correct action for both trigger and non-trigger inputs
- **True positive rate (TPR)**: Correct action when condition IS triggered
- **True negative rate (TNR)**: No conditional action when condition is NOT triggered
- **False positive rate (FPR)**: Conditional action when condition is NOT triggered
- **False negative rate (FNR)**: Missing conditional action when condition IS triggered
- **Cross-type consistency**: Variance of accuracy across instruction types
- **Capacity curve**: Accuracy vs. number of simultaneous conditions

### Statistical Analysis Plan
- Chi-squared test for independence of accuracy across instruction types
- Cochran's Q test for comparing matched binary outcomes across types
- Bootstrap confidence intervals for per-type accuracy
- Spearman correlation between models for per-type difficulty ranking
- Significance level: α = 0.05

## Expected Outcomes
- H1 supported: >15% accuracy range across types (expect negation and nested to be hardest)
- H2 supported: FNR > FPR for most types (models more likely to miss triggers than falsely trigger)
- H3 supported: Clear degradation with more simultaneous conditions
- H4 partially supported: Some consistency in difficulty ranking across models

## Timeline and Milestones
1. Benchmark construction: 30 min
2. API experiment runner: 20 min
3. Verification functions: 20 min
4. Run experiments: 30 min
5. Analysis and visualization: 30 min
6. Documentation: 20 min

## Potential Challenges
- API rate limits → batch with delays
- Ambiguous trigger/non-trigger cases → careful input design
- Verification edge cases → multiple verification strategies per type

## Success Criteria
- Complete benchmark with 8 types, verifiable conditions and actions
- Results from at least 2 models
- Statistical tests showing significant variation across types
- Clear visualization of capacity patterns
