"""
Analysis of In-Context If-Then Capacity experiment results.
Produces statistics, visualizations, and summary tables.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from scipy import stats
from collections import defaultdict

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Style
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams['figure.dpi'] = 150


def load_results():
    with open(os.path.join(RESULTS_DIR, "main_results.json")) as f:
        main = json.load(f)
    with open(os.path.join(RESULTS_DIR, "scaling_results.json")) as f:
        scaling = json.load(f)
    return main, scaling


def analyze_main(results):
    """Analyze main benchmark results."""
    df = pd.DataFrame(results)
    df["correct"] = df["verification"].apply(lambda v: v.get("correct") if v else None)
    df["triggered_action"] = df["verification"].apply(lambda v: v.get("triggered_action") if v else None)

    # Filter out None results
    df = df[df["correct"].notna()].copy()
    df["correct"] = df["correct"].astype(bool)

    print("=" * 70)
    print("MAIN BENCHMARK ANALYSIS")
    print("=" * 70)

    models = df["model"].unique()
    types = sorted(df["type"].unique())

    # ─── Overall accuracy per model ──────────────────────────────────────
    print("\n1. Overall Accuracy by Model")
    print("-" * 40)
    for model in models:
        mdf = df[df["model"] == model]
        acc = mdf["correct"].mean()
        n = len(mdf)
        # Wilson confidence interval
        ci_low, ci_high = _wilson_ci(acc, n)
        print(f"  {model}: {acc:.1%} [{ci_low:.1%}, {ci_high:.1%}] (n={n})")

    # ─── Accuracy by type and model ──────────────────────────────────────
    print("\n2. Accuracy by Instruction Type")
    print("-" * 60)
    type_data = {}
    header = f"{'Type':<15}"
    for model in models:
        header += f" | {model:<20}"
    print(header)
    print("-" * len(header))

    for t in types:
        row = f"{t:<15}"
        type_data[t] = {}
        for model in models:
            mask = (df["model"] == model) & (df["type"] == t)
            acc = df.loc[mask, "correct"].mean()
            n = mask.sum()
            row += f" | {acc:.1%} (n={n})"
            type_data[t][model] = {"accuracy": acc, "n": n}
            row_pad = " " * (20 - len(f"{acc:.1%} (n={n})"))
            row = row.rstrip() + row_pad
        print(row)

    # ─── False positive vs false negative analysis ───────────────────────
    print("\n3. Error Analysis: False Positives vs False Negatives")
    print("-" * 70)
    error_data = {}
    for model in models:
        print(f"\n  Model: {model}")
        print(f"  {'Type':<15} {'FPR':>6} {'FNR':>6} {'TPR':>6} {'TNR':>6}")
        print(f"  {'-'*50}")
        error_data[model] = {}
        for t in types:
            trigger_mask = (df["model"] == model) & (df["type"] == t) & (df["should_trigger"] == True)
            nontrigger_mask = (df["model"] == model) & (df["type"] == t) & (df["should_trigger"] == False)

            trigger_df = df.loc[trigger_mask]
            nontrigger_df = df.loc[nontrigger_mask]

            # TPR: true positive rate (correct when should trigger)
            tpr = trigger_df["correct"].mean() if len(trigger_df) > 0 else float('nan')
            # TNR: true negative rate (correct when should NOT trigger)
            tnr = nontrigger_df["correct"].mean() if len(nontrigger_df) > 0 else float('nan')
            # FNR = 1 - TPR, FPR = 1 - TNR
            fnr = 1 - tpr if not np.isnan(tpr) else float('nan')
            fpr = 1 - tnr if not np.isnan(tnr) else float('nan')

            print(f"  {t:<15} {fpr:>6.1%} {fnr:>6.1%} {tpr:>6.1%} {tnr:>6.1%}")
            error_data[model][t] = {"fpr": fpr, "fnr": fnr, "tpr": tpr, "tnr": tnr}

    # ─── Statistical tests ───────────────────────────────────────────────
    print("\n4. Statistical Tests")
    print("-" * 50)

    for model in models:
        mdf = df[df["model"] == model]
        # Cochran's Q test equivalent: chi-squared test across types
        contingency = []
        for t in types:
            type_df = mdf[mdf["type"] == t]
            correct = type_df["correct"].sum()
            incorrect = len(type_df) - correct
            contingency.append([correct, incorrect])

        contingency = np.array(contingency)
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"\n  {model}:")
        print(f"    Chi-squared test (accuracy varies by type): χ²={chi2:.2f}, df={dof}, p={p_value:.4f}")

        # Effect size: Cramér's V
        n_total = contingency.sum()
        k = min(contingency.shape) - 1
        cramers_v = np.sqrt(chi2 / (n_total * k)) if k > 0 else 0
        print(f"    Cramér's V (effect size): {cramers_v:.3f}")

        # Range of accuracy across types
        type_accs = [mdf[mdf["type"] == t]["correct"].mean() for t in types]
        acc_range = max(type_accs) - min(type_accs)
        print(f"    Accuracy range across types: {acc_range:.1%}")
        print(f"    Best type: {types[np.argmax(type_accs)]} ({max(type_accs):.1%})")
        print(f"    Worst type: {types[np.argmin(type_accs)]} ({min(type_accs):.1%})")

    # ─── Cross-model consistency ─────────────────────────────────────────
    if len(models) >= 2:
        print("\n5. Cross-Model Consistency")
        print("-" * 50)
        model_accs = {}
        for model in models:
            mdf = df[df["model"] == model]
            model_accs[model] = [mdf[mdf["type"] == t]["correct"].mean() for t in types]

        m1, m2 = models[0], models[1]
        rho, p_rho = stats.spearmanr(model_accs[m1], model_accs[m2])
        print(f"  Spearman correlation (type difficulty ranking):")
        print(f"    {m1} vs {m2}: ρ={rho:.3f}, p={p_rho:.4f}")

    return df, type_data, error_data


def analyze_scaling(results):
    """Analyze scaling benchmark results."""
    df = pd.DataFrame(results)
    df["correct"] = df["verification"].apply(lambda v: v.get("correct") if v else None)
    df = df[df["correct"].notna()].copy()
    df["correct"] = df["correct"].astype(bool)

    print("\n" + "=" * 70)
    print("SCALING ANALYSIS")
    print("=" * 70)

    models = df["model"].unique()

    print(f"\n{'Model':<20} {'1 cond':>10} {'2 cond':>10} {'4 cond':>10}")
    print("-" * 55)

    scaling_data = {}
    for model in models:
        mdf = df[df["model"] == model]
        row = f"{model:<20}"
        scaling_data[model] = {}
        for nc in [1, 2, 4]:
            ncdf = mdf[mdf["num_conditions"] == nc]
            if len(ncdf) > 0:
                acc = ncdf["correct"].mean()
                row += f" {acc:>10.1%}"
                scaling_data[model][nc] = acc
            else:
                row += f" {'N/A':>10}"
        print(row)

    # Per-marker accuracy for scaling
    print("\n  Per-marker accuracy (2 and 4 conditions):")
    for model in models:
        mdf = df[df["model"] == model]
        for nc in [2, 4]:
            ncdf = mdf[mdf["num_conditions"] == nc]
            total_markers = 0
            correct_markers = 0
            for _, row in ncdf.iterrows():
                v = row["verification"]
                if "marker_results" in v:
                    for mr in v["marker_results"]:
                        total_markers += 1
                        if mr["correct"]:
                            correct_markers += 1
            if total_markers > 0:
                print(f"    {model}, {nc} conds: {correct_markers}/{total_markers} markers correct ({correct_markers/total_markers:.1%})")

    return df, scaling_data


def plot_results(main_df, type_data, error_data, scaling_data):
    """Generate all visualizations."""
    models = main_df["model"].unique()
    types = sorted(main_df["type"].unique())

    # ─── Plot 1: Accuracy by type and model ──────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(types))
    width = 0.35
    for i, model in enumerate(models):
        accs = [type_data[t][model]["accuracy"] for t in types]
        bars = ax.bar(x + i * width, accs, width, label=model, alpha=0.85)
        for bar, acc in zip(bars, accs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{acc:.0%}', ha='center', va='bottom', fontsize=8)
    ax.set_xlabel("Instruction Type")
    ax.set_ylabel("Accuracy")
    ax.set_title("If-Then Conditional Instruction Accuracy by Type")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(types, rotation=30, ha='right')
    ax.set_ylim(0, 1.15)
    ax.legend()
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='chance')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "accuracy_by_type.png"))
    plt.close()
    print(f"\nSaved: {PLOTS_DIR}/accuracy_by_type.png")

    # ─── Plot 2: FPR vs FNR heatmap ─────────────────────────────────────
    for model in models:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fpr_data = [error_data[model][t]["fpr"] for t in types]
        fnr_data = [error_data[model][t]["fnr"] for t in types]

        colors_fpr = ['#ff6b6b' if v > 0.3 else '#ffd93d' if v > 0.1 else '#6bcb77' for v in fpr_data]
        colors_fnr = ['#ff6b6b' if v > 0.3 else '#ffd93d' if v > 0.1 else '#6bcb77' for v in fnr_data]

        axes[0].barh(types, fpr_data, color=colors_fpr, alpha=0.85)
        axes[0].set_xlabel("False Positive Rate")
        axes[0].set_title(f"FPR by Type ({model})")
        axes[0].set_xlim(0, 1)

        axes[1].barh(types, fnr_data, color=colors_fnr, alpha=0.85)
        axes[1].set_xlabel("False Negative Rate")
        axes[1].set_title(f"FNR by Type ({model})")
        axes[1].set_xlim(0, 1)

        plt.tight_layout()
        safe_model = model.replace(".", "_")
        plt.savefig(os.path.join(PLOTS_DIR, f"fpr_fnr_{safe_model}.png"))
        plt.close()
        print(f"Saved: {PLOTS_DIR}/fpr_fnr_{safe_model}.png")

    # ─── Plot 3: Trigger vs Non-trigger accuracy ─────────────────────────
    fig, axes = plt.subplots(1, len(models), figsize=(7 * len(models), 6))
    if len(models) == 1:
        axes = [axes]
    for ax, model in zip(axes, models):
        trigger_accs = []
        nontrigger_accs = []
        for t in types:
            mdf = main_df[(main_df["model"] == model) & (main_df["type"] == t)]
            trigger_acc = mdf[mdf["should_trigger"] == True]["correct"].mean()
            nontrigger_acc = mdf[mdf["should_trigger"] == False]["correct"].mean()
            trigger_accs.append(trigger_acc)
            nontrigger_accs.append(nontrigger_acc)

        x = np.arange(len(types))
        ax.bar(x - 0.2, trigger_accs, 0.4, label='Trigger (TPR)', color='#4ecdc4', alpha=0.85)
        ax.bar(x + 0.2, nontrigger_accs, 0.4, label='Non-trigger (TNR)', color='#ff6b6b', alpha=0.85)
        ax.set_xlabel("Instruction Type")
        ax.set_ylabel("Accuracy")
        ax.set_title(f"Trigger vs Non-Trigger Accuracy ({model})")
        ax.set_xticks(x)
        ax.set_xticklabels(types, rotation=30, ha='right')
        ax.set_ylim(0, 1.15)
        ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "trigger_vs_nontrigger.png"))
    plt.close()
    print(f"Saved: {PLOTS_DIR}/trigger_vs_nontrigger.png")

    # ─── Plot 4: Scaling curve ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    for model in models:
        if model in scaling_data:
            conds = sorted(scaling_data[model].keys())
            accs = [scaling_data[model][c] for c in conds]
            ax.plot(conds, accs, 'o-', label=model, linewidth=2, markersize=8)
    ax.set_xlabel("Number of Simultaneous Conditions")
    ax.set_ylabel("Accuracy")
    ax.set_title("Accuracy vs. Number of Conditions (Capacity Curve)")
    ax.set_xticks([1, 2, 4])
    ax.set_ylim(0, 1.1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "scaling_curve.png"))
    plt.close()
    print(f"Saved: {PLOTS_DIR}/scaling_curve.png")

    # ─── Plot 5: Cross-model comparison scatter ──────────────────────────
    if len(models) >= 2:
        fig, ax = plt.subplots(figsize=(7, 7))
        m1, m2 = models[0], models[1]
        accs1 = [main_df[(main_df["model"] == m1) & (main_df["type"] == t)]["correct"].mean() for t in types]
        accs2 = [main_df[(main_df["model"] == m2) & (main_df["type"] == t)]["correct"].mean() for t in types]

        ax.scatter(accs1, accs2, s=100, zorder=5)
        for i, t in enumerate(types):
            ax.annotate(t, (accs1[i], accs2[i]), textcoords="offset points",
                        xytext=(5, 5), fontsize=9)
        ax.plot([0, 1], [0, 1], '--', color='gray', alpha=0.5)
        ax.set_xlabel(f"Accuracy ({m1})")
        ax.set_ylabel(f"Accuracy ({m2})")
        ax.set_title("Cross-Model Difficulty Correlation")
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "cross_model_scatter.png"))
        plt.close()
        print(f"Saved: {PLOTS_DIR}/cross_model_scatter.png")

    # ─── Plot 6: Overall summary radar chart ─────────────────────────────
    for model in models:
        accs = [type_data[t][model]["accuracy"] for t in types]
        angles = np.linspace(0, 2 * np.pi, len(types), endpoint=False).tolist()
        accs_plot = accs + [accs[0]]
        angles_plot = angles + [angles[0]]

        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
        ax.plot(angles_plot, accs_plot, 'o-', linewidth=2)
        ax.fill(angles_plot, accs_plot, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles), types)
        ax.set_ylim(0, 1)
        ax.set_title(f"If-Then Capacity Profile ({model})")
        plt.tight_layout()
        safe_model = model.replace(".", "_")
        plt.savefig(os.path.join(PLOTS_DIR, f"radar_{safe_model}.png"))
        plt.close()
        print(f"Saved: {PLOTS_DIR}/radar_{safe_model}.png")


def _wilson_ci(p, n, z=1.96):
    """Wilson confidence interval for a proportion."""
    if n == 0:
        return 0, 0
    denom = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denom
    spread = z * np.sqrt((p*(1-p) + z**2/(4*n)) / n) / denom
    return max(0, center - spread), min(1, center + spread)


def save_summary_table(main_df, type_data, error_data, scaling_data):
    """Save a summary table as JSON and markdown."""
    models = main_df["model"].unique()
    types = sorted(main_df["type"].unique())

    summary = {
        "overall": {},
        "by_type": type_data,
        "errors": {},
        "scaling": scaling_data,
    }

    for model in models:
        mdf = main_df[main_df["model"] == model]
        summary["overall"][model] = {
            "accuracy": float(mdf["correct"].mean()),
            "n": int(len(mdf)),
        }
        summary["errors"][model] = {}
        for t in types:
            summary["errors"][model][t] = {
                k: float(v) if not np.isnan(v) else None
                for k, v in error_data[model][t].items()
            }

    with open(os.path.join(RESULTS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSaved: {RESULTS_DIR}/summary.json")


def main():
    main_results, scaling_results = load_results()
    main_df, type_data, error_data = analyze_main(main_results)
    scaling_df, scaling_data = analyze_scaling(scaling_results)
    plot_results(main_df, type_data, error_data, scaling_data)
    save_summary_table(main_df, type_data, error_data, scaling_data)
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
