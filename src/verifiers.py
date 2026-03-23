"""
Verification functions for conditional instruction compliance.

Each verifier returns a dict with:
- "correct": bool — did the model comply correctly?
- "triggered_action": bool — did the model perform the conditional action?
- "details": str — explanation
"""

import re
import json


def verify(test_case, response):
    """Dispatch to the appropriate verifier."""
    verifier_name = test_case["verifier"]
    should_trigger = test_case["should_trigger"]
    args = test_case.get("verifier_args", {})

    verifier_fn = VERIFIERS.get(verifier_name)
    if not verifier_fn:
        return {"correct": None, "triggered_action": None, "details": f"Unknown verifier: {verifier_name}"}

    return verifier_fn(test_case, response, should_trigger, args)


# ─── Type 1: Keyword-conditional ─────────────────────────────────────────────

def starts_with_if_keyword(tc, response, should_trigger, args):
    keyword = args["keyword"].lower()
    prefix = args["prefix"]
    input_has_keyword = keyword in tc["input"].lower()
    response_has_prefix = response.strip().startswith(prefix)

    if should_trigger:
        correct = response_has_prefix
        return {"correct": correct, "triggered_action": response_has_prefix,
                "details": f"Input has '{keyword}': {input_has_keyword}, response starts with '{prefix}': {response_has_prefix}"}
    else:
        correct = not response_has_prefix
        return {"correct": correct, "triggered_action": response_has_prefix,
                "details": f"Input lacks '{keyword}': {not input_has_keyword}, response starts with '{prefix}': {response_has_prefix}"}


def ends_with_if_keyword(tc, response, should_trigger, args):
    keyword = args["keyword"].lower()
    suffix = args["suffix"]
    response_has_suffix = response.strip().endswith(suffix)

    if should_trigger:
        correct = response_has_suffix
    else:
        correct = not response_has_suffix
    return {"correct": correct, "triggered_action": response_has_suffix,
            "details": f"Should trigger: {should_trigger}, response ends with '{suffix}': {response_has_suffix}"}


def numbered_list_if_keyword(tc, response, should_trigger, args):
    keyword = args["keyword"].lower()
    # Check for numbered list: lines starting with "1." "2." etc.
    has_numbered = bool(re.search(r'^\s*1[.)]\s', response, re.MULTILINE)) and \
                   bool(re.search(r'^\s*2[.)]\s', response, re.MULTILINE))

    if should_trigger:
        correct = has_numbered
    else:
        correct = not has_numbered
    return {"correct": correct, "triggered_action": has_numbered,
            "details": f"Should trigger: {should_trigger}, has numbered list: {has_numbered}"}


# ─── Type 2: Format-conditional ──────────────────────────────────────────────

def json_if_about_person(tc, response, should_trigger, args):
    # Try to detect JSON in response
    has_json = False
    try:
        # Look for JSON block
        json_match = re.search(r'\{[^{}]*"name"[^{}]*\}', response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            has_json = "name" in parsed
    except (json.JSONDecodeError, AttributeError):
        pass
    # Also check for ```json blocks
    if not has_json:
        json_block = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL)
        if json_block:
            try:
                parsed = json.loads(json_block.group(1))
                has_json = "name" in parsed
            except json.JSONDecodeError:
                pass

    if should_trigger:
        correct = has_json
    else:
        correct = not has_json
    return {"correct": correct, "triggered_action": has_json,
            "details": f"Should trigger: {should_trigger}, has JSON with 'name': {has_json}"}


def yes_no_start_if_yesno_question(tc, response, should_trigger, args):
    stripped = response.strip()
    starts_yes_no = stripped.startswith("Yes.") or stripped.startswith("No.")

    if should_trigger:
        correct = starts_yes_no
    else:
        correct = not starts_yes_no
    return {"correct": correct, "triggered_action": starts_yes_no,
            "details": f"Should trigger: {should_trigger}, starts Yes./No.: {starts_yes_no}"}


def bullets_if_country(tc, response, should_trigger, args):
    # Check for bullet points (-, *, •)
    bullet_lines = re.findall(r'^\s*[-*•]\s+\S', response, re.MULTILINE)
    has_bullets = len(bullet_lines) >= 2

    if should_trigger:
        correct = has_bullets
    else:
        correct = not has_bullets
    return {"correct": correct, "triggered_action": has_bullets,
            "details": f"Should trigger: {should_trigger}, has bullets: {has_bullets} ({len(bullet_lines)} found)"}


# ─── Type 3: Length-conditional ──────────────────────────────────────────────

def _count_sentences(text):
    """Count sentences (rough heuristic)."""
    # Split on sentence-ending punctuation followed by space or end
    sentences = re.split(r'[.!?]+(?:\s|$)', text.strip())
    return len([s for s in sentences if s.strip()])


def length_by_input_wordcount(tc, response, should_trigger, args):
    input_words = len(tc["input"].split())
    threshold = args["threshold"]
    is_single_word = input_words <= threshold
    sentences = _count_sentences(response)

    if should_trigger:  # single word input → one sentence
        correct = sentences <= 2  # allow slight tolerance
    else:  # multi-word input → at least 3 sentences
        correct = sentences >= 3
    return {"correct": correct, "triggered_action": sentences <= 2,
            "details": f"Input words: {input_words}, response sentences: {sentences}, should_trigger: {should_trigger}"}


def inverse_length_response(tc, response, should_trigger, args):
    input_words = len(tc["input"].split())
    response_words = len(response.split())
    input_threshold = args["input_threshold"]

    if should_trigger:  # long input → short response
        correct = response_words <= args["short_response_max"] + 10  # some tolerance
    else:  # short input → long response
        correct = response_words >= args["long_response_min"] - 10  # some tolerance
    return {"correct": correct, "triggered_action": response_words <= args["short_response_max"] + 10,
            "details": f"Input words: {input_words}, response words: {response_words}, should_trigger: {should_trigger}"}


# ─── Type 4: Content-conditional ─────────────────────────────────────────────

def math_fact_if_number(tc, response, should_trigger, args):
    has_math_fact = "math fact:" in response.lower() or "math fact :" in response.lower()

    if should_trigger:
        correct = has_math_fact
    else:
        correct = not has_math_fact
    return {"correct": correct, "triggered_action": has_math_fact,
            "details": f"Should trigger: {should_trigger}, has 'Math fact:': {has_math_fact}"}


def hex_code_if_color(tc, response, should_trigger, args):
    has_hex = bool(re.search(r'#[0-9a-fA-F]{6}\b', response))

    if should_trigger:
        correct = has_hex
    else:
        correct = not has_hex
    return {"correct": correct, "triggered_action": has_hex,
            "details": f"Should trigger: {should_trigger}, has hex code: {has_hex}"}


def animal_fact_if_animal(tc, response, should_trigger, args):
    has_fun_fact = "fun animal fact:" in response.lower() or "fun animal fact :" in response.lower()

    if should_trigger:
        correct = has_fun_fact
    else:
        correct = not has_fun_fact
    return {"correct": correct, "triggered_action": has_fun_fact,
            "details": f"Should trigger: {should_trigger}, has 'Fun animal fact:': {has_fun_fact}"}


# ─── Type 5: Negation-conditional ────────────────────────────────────────────

def uppercase_if_no_question_mark(tc, response, should_trigger, args):
    # Check if response is all uppercase (excluding punctuation, numbers, whitespace)
    alpha_chars = [c for c in response if c.isalpha()]
    if not alpha_chars:
        is_upper = False
    else:
        uppercase_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        is_upper = uppercase_ratio > 0.85  # allow some tolerance

    if should_trigger:  # no question mark → should be uppercase
        correct = is_upper
    else:  # has question mark → should NOT be uppercase
        correct = not is_upper
    return {"correct": correct, "triggered_action": is_upper,
            "details": f"Should trigger: {should_trigger}, is uppercase: {is_upper}"}


def food_tangent_if_no_food(tc, response, should_trigger, args):
    has_phrase = "speaking of food," in response.lower()

    if should_trigger:  # no food in input → should include food tangent
        correct = has_phrase
    else:  # food in input → should NOT include food tangent
        correct = not has_phrase
    return {"correct": correct, "triggered_action": has_phrase,
            "details": f"Should trigger: {should_trigger}, has 'Speaking of food,': {has_phrase}"}


def please_reminder_if_no_please(tc, response, should_trigger, args):
    has_reminder = response.strip().startswith("Remember to say please!")

    if should_trigger:  # no 'please' → should have reminder
        correct = has_reminder
    else:  # has 'please' → should NOT have reminder
        correct = not has_reminder
    return {"correct": correct, "triggered_action": has_reminder,
            "details": f"Should trigger: {should_trigger}, has reminder: {has_reminder}"}


# ─── Type 6: Nested-conditional ──────────────────────────────────────────────

def nested_beverage(tc, response, should_trigger, args):
    hot_beverages = ["coffee", "tea", "hot chocolate", "cocoa"]
    cold_beverages = ["juice", "soda", "smoothie", "lemonade"]

    input_lower = tc["input"].lower()
    has_hot = any(b in input_lower for b in hot_beverages)
    has_cold = any(b in input_lower for b in cold_beverages)

    ends_warm = "enjoy it warm!" in response.lower()
    ends_chilled = "best served chilled!" in response.lower()

    if should_trigger:
        if has_hot:
            correct = ends_warm
        elif has_cold:
            correct = ends_chilled
        else:
            correct = False
    else:
        correct = not ends_warm and not ends_chilled
    triggered = ends_warm or ends_chilled
    return {"correct": correct, "triggered_action": triggered,
            "details": f"hot: {has_hot}, cold: {has_cold}, ends_warm: {ends_warm}, ends_chilled: {ends_chilled}"}


def nested_number_parity(tc, response, should_trigger, args):
    # Find numbers in input
    numbers = re.findall(r'\d+', tc["input"])
    paragraphs = [p.strip() for p in response.strip().split('\n\n') if p.strip()]
    num_paragraphs = len(paragraphs)

    if should_trigger and numbers:
        first_num = int(numbers[0])
        if first_num % 2 == 0:
            correct = num_paragraphs == 2
        else:
            correct = num_paragraphs == 3
    elif not should_trigger:
        correct = num_paragraphs == 1
    else:
        correct = False

    return {"correct": correct, "triggered_action": num_paragraphs > 1,
            "details": f"Numbers found: {numbers}, paragraphs: {num_paragraphs}, should_trigger: {should_trigger}"}


# ─── Type 7: Multi-condition AND ─────────────────────────────────────────────

def prefix_if_both_conditions(tc, response, should_trigger, args):
    prefix = args["prefix"]
    conditions = args["conditions"]
    input_lower = tc["input"].lower()
    all_met = all(c.lower() in input_lower for c in conditions)
    has_prefix = response.strip().startswith(prefix)

    if should_trigger:
        correct = has_prefix
    else:
        correct = not has_prefix
    return {"correct": correct, "triggered_action": has_prefix,
            "details": f"All conditions met: {all_met}, has prefix: {has_prefix}, should_trigger: {should_trigger}"}


def season_sport_recommendation(tc, response, should_trigger, args):
    # Check if response contains a recommendation-like phrase
    rec_phrases = ["recommend", "great time to watch", "perfect season", "enjoy watching",
                   "catch a game", "great for", "best time"]
    has_recommendation = any(p in response.lower() for p in rec_phrases)

    if should_trigger:
        correct = has_recommendation
    else:
        correct = not has_recommendation
    return {"correct": correct, "triggered_action": has_recommendation,
            "details": f"Should trigger: {should_trigger}, has recommendation: {has_recommendation}"}


# ─── Type 8: Multi-condition OR ──────────────────────────────────────────────

def prefix_if_either_keyword(tc, response, should_trigger, args):
    keywords = args["keywords"]
    prefix = args["prefix"]
    input_lower = tc["input"].lower()
    any_present = any(k.lower() in input_lower for k in keywords)
    has_prefix = response.strip().startswith(prefix)

    if should_trigger:
        correct = has_prefix
    else:
        correct = not has_prefix
    return {"correct": correct, "triggered_action": has_prefix,
            "details": f"Any keyword present: {any_present}, has prefix: {has_prefix}, should_trigger: {should_trigger}"}


def greeting_if_time_of_day(tc, response, should_trigger, args):
    has_greeting = ("good morning" in response.lower()[:50] or
                    "good evening" in response.lower()[:50])

    if should_trigger:
        correct = has_greeting
    else:
        correct = not has_greeting
    return {"correct": correct, "triggered_action": has_greeting,
            "details": f"Should trigger: {should_trigger}, has time greeting: {has_greeting}"}


# ─── Scaling verifier ────────────────────────────────────────────────────────

def verify_scaling(test_case, response):
    """Verify scaling benchmark test cases."""
    results = []
    for marker in test_case.get("expected_markers", []):
        present = marker in response
        results.append({"marker": marker, "expected": True, "present": present, "correct": present})
    for marker in test_case.get("absent_markers", []):
        present = marker in response
        results.append({"marker": marker, "expected": False, "present": present, "correct": not present})

    all_correct = all(r["correct"] for r in results)
    return {"correct": all_correct, "marker_results": results,
            "details": f"Markers: {results}"}


# ─── Registry ────────────────────────────────────────────────────────────────

VERIFIERS = {
    "starts_with_if_keyword": starts_with_if_keyword,
    "ends_with_if_keyword": ends_with_if_keyword,
    "numbered_list_if_keyword": numbered_list_if_keyword,
    "json_if_about_person": json_if_about_person,
    "yes_no_start_if_yesno_question": yes_no_start_if_yesno_question,
    "bullets_if_country": bullets_if_country,
    "length_by_input_wordcount": length_by_input_wordcount,
    "inverse_length_response": inverse_length_response,
    "math_fact_if_number": math_fact_if_number,
    "hex_code_if_color": hex_code_if_color,
    "animal_fact_if_animal": animal_fact_if_animal,
    "uppercase_if_no_question_mark": uppercase_if_no_question_mark,
    "food_tangent_if_no_food": food_tangent_if_no_food,
    "please_reminder_if_no_please": please_reminder_if_no_please,
    "nested_beverage": nested_beverage,
    "nested_number_parity": nested_number_parity,
    "prefix_if_both_conditions": prefix_if_both_conditions,
    "season_sport_recommendation": season_sport_recommendation,
    "prefix_if_either_keyword": prefix_if_either_keyword,
    "greeting_if_time_of_day": greeting_if_time_of_day,
}
