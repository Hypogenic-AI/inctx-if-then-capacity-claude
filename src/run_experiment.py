"""
Run the If-Then Capacity experiment against real LLM APIs.
"""

import json
import os
import sys
import time
import random
import asyncio
from datetime import datetime

import openai

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))
from benchmark import build_benchmark, build_scaling_benchmark
from verifiers import verify, verify_scaling

# Configuration
MODELS = [
    "gpt-4.1",
    "gpt-4o-mini",
]
TEMPERATURE = 0.0  # deterministic
MAX_TOKENS = 500
SEED = 42
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

random.seed(SEED)


def call_model(client, model, system_prompt, user_message, max_retries=3):
    """Call an LLM model with retry logic."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                seed=SEED,
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"  Retry {attempt + 1} after error: {e}")
                time.sleep(wait_time)
            else:
                print(f"  FAILED after {max_retries} retries: {e}")
                return None


def run_main_benchmark(client, model, test_cases):
    """Run the main conditional instruction benchmark."""
    results = []
    total = len(test_cases)

    for i, tc in enumerate(test_cases):
        if (i + 1) % 10 == 0:
            print(f"  [{model}] {i+1}/{total}...")

        system_prompt = (
            "You are a helpful assistant. Follow the instructions below precisely.\n\n"
            f"INSTRUCTION: {tc['instruction']}"
        )
        user_message = tc["input"]

        response = call_model(client, model, system_prompt, user_message)
        if response is None:
            results.append({**tc, "model": model, "response": None, "verification": {"correct": None}})
            continue

        verification = verify(tc, response)
        results.append({
            **tc,
            "model": model,
            "response": response,
            "verification": verification,
        })

    return results


def run_scaling_benchmark(client, model, test_cases):
    """Run the scaling benchmark."""
    results = []
    total = len(test_cases)

    for i, tc in enumerate(test_cases):
        system_prompt = (
            "You are a helpful assistant. Follow ALL of the instructions below precisely.\n\n"
            f"INSTRUCTIONS: {tc['instruction']}"
        )
        user_message = tc["input"]

        response = call_model(client, model, system_prompt, user_message)
        if response is None:
            results.append({**tc, "model": model, "response": None, "verification": {"correct": None}})
            continue

        verification = verify_scaling(tc, response)
        results.append({
            **tc,
            "model": model,
            "response": response,
            "verification": verification,
        })

    return results


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Build benchmarks
    print("Building benchmark...")
    main_cases = build_benchmark()
    scaling_cases = build_scaling_benchmark()
    print(f"  Main benchmark: {len(main_cases)} test cases")
    print(f"  Scaling benchmark: {len(scaling_cases)} test cases")

    # Save benchmarks
    with open(os.path.join(RESULTS_DIR, "benchmark.json"), "w") as f:
        json.dump(main_cases, f, indent=2)
    with open(os.path.join(RESULTS_DIR, "scaling_benchmark.json"), "w") as f:
        json.dump(scaling_cases, f, indent=2)

    # Initialize client
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    all_main_results = []
    all_scaling_results = []

    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"Running model: {model}")
        print(f"{'='*60}")

        # Main benchmark
        print(f"\n--- Main benchmark ({len(main_cases)} cases) ---")
        start = time.time()
        main_results = run_main_benchmark(client, model, main_cases)
        elapsed = time.time() - start
        print(f"  Completed in {elapsed:.1f}s")
        all_main_results.extend(main_results)

        # Quick summary
        correct = sum(1 for r in main_results if r["verification"]["correct"])
        total = sum(1 for r in main_results if r["verification"]["correct"] is not None)
        print(f"  Overall accuracy: {correct}/{total} = {correct/total:.1%}")

        # Scaling benchmark
        print(f"\n--- Scaling benchmark ({len(scaling_cases)} cases) ---")
        start = time.time()
        scaling_results = run_scaling_benchmark(client, model, scaling_cases)
        elapsed = time.time() - start
        print(f"  Completed in {elapsed:.1f}s")
        all_scaling_results.extend(scaling_results)

    # Save all results
    results_file = os.path.join(RESULTS_DIR, "main_results.json")
    with open(results_file, "w") as f:
        json.dump(all_main_results, f, indent=2, default=str)
    print(f"\nMain results saved to {results_file}")

    scaling_file = os.path.join(RESULTS_DIR, "scaling_results.json")
    with open(scaling_file, "w") as f:
        json.dump(all_scaling_results, f, indent=2, default=str)
    print(f"Scaling results saved to {scaling_file}")

    # Save config
    config = {
        "models": MODELS,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "seed": SEED,
        "timestamp": datetime.now().isoformat(),
        "num_main_cases": len(main_cases),
        "num_scaling_cases": len(scaling_cases),
        "python_version": sys.version,
        "openai_version": openai.__version__,
    }
    with open(os.path.join(RESULTS_DIR, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    print("\nDone! Run src/analyze.py for analysis.")


if __name__ == "__main__":
    main()
