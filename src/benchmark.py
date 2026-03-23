"""
Benchmark for In-Context If-Then Capacity.

Defines 8 types of conditional instructions, each with:
- Instruction template
- Trigger inputs (condition should activate)
- Non-trigger inputs (condition should NOT activate)
- Verification function to check compliance
"""

import json
import random

random.seed(42)


def build_benchmark():
    """Build the full benchmark: list of test cases."""
    types = get_instruction_types()
    test_cases = []

    for type_info in types:
        type_name = type_info["type"]
        for inst_idx, instruction_set in enumerate(type_info["instructions"]):
            instruction = instruction_set["instruction"]
            verifier_name = instruction_set["verifier"]

            # Trigger inputs (condition should fire)
            for inp_idx, inp in enumerate(instruction_set["trigger_inputs"]):
                test_cases.append({
                    "id": f"{type_name}_{inst_idx}_trigger_{inp_idx}",
                    "type": type_name,
                    "instruction": instruction,
                    "input": inp,
                    "should_trigger": True,
                    "verifier": verifier_name,
                    "verifier_args": instruction_set.get("verifier_args", {}),
                })

            # Non-trigger inputs (condition should NOT fire)
            for inp_idx, inp in enumerate(instruction_set["non_trigger_inputs"]):
                test_cases.append({
                    "id": f"{type_name}_{inst_idx}_nontrigger_{inp_idx}",
                    "type": type_name,
                    "instruction": instruction,
                    "input": inp,
                    "should_trigger": False,
                    "verifier": verifier_name,
                    "verifier_args": instruction_set.get("verifier_args", {}),
                })

    return test_cases


def get_instruction_types():
    """Return all 8 instruction types with their test cases."""
    return [
        # Type 1: Keyword-conditional
        {
            "type": "keyword",
            "description": "If input contains a specific keyword, modify output format",
            "instructions": [
                {
                    "instruction": "If the user's message contains the word 'urgent', start your response with 'PRIORITY: ' (exactly). Otherwise, just answer normally.",
                    "verifier": "starts_with_if_keyword",
                    "verifier_args": {"keyword": "urgent", "prefix": "PRIORITY: "},
                    "trigger_inputs": [
                        "This is an urgent matter regarding the budget deadline.",
                        "I need urgent help with my account settings.",
                        "The urgent request from the client needs attention.",
                    ],
                    "non_trigger_inputs": [
                        "Can you explain how photosynthesis works?",
                        "What is the capital of France?",
                        "Tell me about the history of jazz music.",
                    ],
                },
                {
                    "instruction": "If the user's message contains the word 'recipe', end your response with 'Bon appetit!' on a new line. Otherwise, respond normally.",
                    "verifier": "ends_with_if_keyword",
                    "verifier_args": {"keyword": "recipe", "suffix": "Bon appetit!"},
                    "trigger_inputs": [
                        "Can you share a recipe for chocolate cake?",
                        "I need a recipe that uses chicken and rice.",
                        "What's your favorite pasta recipe?",
                    ],
                    "non_trigger_inputs": [
                        "How do I fix a flat tire?",
                        "Explain the theory of relativity.",
                        "What programming language should I learn first?",
                    ],
                },
                {
                    "instruction": "If the user's message contains the word 'compare', use a numbered list in your response. Otherwise, answer in a single paragraph.",
                    "verifier": "numbered_list_if_keyword",
                    "verifier_args": {"keyword": "compare"},
                    "trigger_inputs": [
                        "Compare Python and JavaScript for web development.",
                        "Can you compare the climates of London and Tokyo?",
                        "I want to compare electric cars vs hybrid cars.",
                    ],
                    "non_trigger_inputs": [
                        "What is machine learning?",
                        "Tell me about the Great Wall of China.",
                        "How does a solar panel work?",
                    ],
                },
            ],
        },
        # Type 2: Format-conditional
        {
            "type": "format",
            "description": "If input asks about certain topics, respond in a specific format",
            "instructions": [
                {
                    "instruction": "If the user asks about a person, respond in JSON format with keys 'name', 'known_for', and 'era'. Otherwise, respond in plain text.",
                    "verifier": "json_if_about_person",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Tell me about Albert Einstein.",
                        "Who was Cleopatra?",
                        "What did Marie Curie accomplish?",
                    ],
                    "non_trigger_inputs": [
                        "What causes earthquakes?",
                        "Explain how WiFi works.",
                        "What is the tallest mountain in the world?",
                    ],
                },
                {
                    "instruction": "If the user asks a yes/no question, respond with exactly 'Yes.' or 'No.' as the first word followed by a period, then explain. Otherwise, answer freely.",
                    "verifier": "yes_no_start_if_yesno_question",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Is the Earth round?",
                        "Can humans breathe underwater?",
                        "Do cats see in color?",
                    ],
                    "non_trigger_inputs": [
                        "How many planets are in the solar system?",
                        "What is the meaning of life?",
                        "Describe the process of making cheese.",
                    ],
                },
                {
                    "instruction": "If the user asks about a country, respond using bullet points. Otherwise, respond in a single paragraph.",
                    "verifier": "bullets_if_country",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Tell me about Japan.",
                        "What should I know about Brazil?",
                        "Describe the culture of Italy.",
                    ],
                    "non_trigger_inputs": [
                        "How does gravity work?",
                        "What is an algorithm?",
                        "Explain the water cycle.",
                    ],
                },
            ],
        },
        # Type 3: Length-conditional
        {
            "type": "length",
            "description": "If input has certain properties, control response length",
            "instructions": [
                {
                    "instruction": "If the user's message is a single word, respond in exactly one sentence (ending with a period). If it's longer, respond in at least three sentences.",
                    "verifier": "length_by_input_wordcount",
                    "verifier_args": {"threshold": 1, "short_max_sentences": 1, "long_min_sentences": 3},
                    "trigger_inputs": [
                        "Photosynthesis",
                        "Democracy",
                        "Blockchain",
                    ],
                    "non_trigger_inputs": [
                        "Can you explain how photosynthesis works in plants?",
                        "What are the main principles of democracy?",
                        "How does blockchain technology ensure data security?",
                    ],
                },
                {
                    "instruction": "If the user's question contains more than 20 words, give a brief answer in under 30 words. If it's short (20 words or fewer), give a detailed answer of at least 80 words.",
                    "verifier": "inverse_length_response",
                    "verifier_args": {"input_threshold": 20, "short_response_max": 30, "long_response_min": 80},
                    "trigger_inputs": [
                        "I was wondering if you could please explain to me in great detail how exactly the process of nuclear fusion works inside the core of stars like our sun and what elements are produced during this process?",
                        "Given all the recent advancements in artificial intelligence and machine learning technology over the past decade, what do you think will be the most significant breakthrough in the next five years?",
                        "Could you please provide me with a comprehensive and detailed explanation about the various different types of renewable energy sources that are currently being developed and used around the world today?",
                    ],
                    "non_trigger_inputs": [
                        "What is gravity?",
                        "Why is the sky blue?",
                        "How do computers work?",
                    ],
                },
            ],
        },
        # Type 4: Content-conditional
        {
            "type": "content",
            "description": "If input mentions specific content, include specific content in response",
            "instructions": [
                {
                    "instruction": "If the user mentions any number in their message, include a mathematical fact in your response (prefixed with 'Math fact:'). Otherwise, answer normally without any math references.",
                    "verifier": "math_fact_if_number",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "I have 3 cats at home.",
                        "The building is 50 stories tall, tell me about skyscrapers.",
                        "What happened in the year 1969?",
                    ],
                    "non_trigger_inputs": [
                        "Tell me about cats.",
                        "What makes a building a skyscraper?",
                        "What happened when humans first walked on the moon?",
                    ],
                },
                {
                    "instruction": "If the user mentions a color in their message, include the hex code for that color somewhere in your response (formatted as #XXXXXX). Otherwise, respond normally.",
                    "verifier": "hex_code_if_color",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "What emotions does the color blue evoke?",
                        "I painted my room red last weekend.",
                        "Why do plants appear green?",
                    ],
                    "non_trigger_inputs": [
                        "How do emotions affect decision-making?",
                        "What's the best way to paint a room?",
                        "How do plants produce energy?",
                    ],
                },
                {
                    "instruction": "If the user mentions an animal, end your response with 'Fun animal fact: ' followed by a fact about that animal. Otherwise, just answer the question.",
                    "verifier": "animal_fact_if_animal",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "How fast can a cheetah run?",
                        "I saw a dolphin at the aquarium today.",
                        "Are elephants really afraid of mice?",
                    ],
                    "non_trigger_inputs": [
                        "How fast is the speed of light?",
                        "I visited the aquarium today.",
                        "What causes fear in humans?",
                    ],
                },
            ],
        },
        # Type 5: Negation-conditional
        {
            "type": "negation",
            "description": "If input does NOT have a property, modify output",
            "instructions": [
                {
                    "instruction": "If the user's message does NOT contain a question mark, respond entirely in uppercase letters. If it contains a question mark, respond normally in mixed case.",
                    "verifier": "uppercase_if_no_question_mark",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Tell me about the solar system.",
                        "Explain quantum computing.",
                        "Describe the Amazon rainforest.",
                    ],
                    "non_trigger_inputs": [
                        "What is the solar system?",
                        "Can you explain quantum computing?",
                        "Where is the Amazon rainforest?",
                    ],
                },
                {
                    "instruction": "If the user's message does NOT mention any food item, include the phrase 'Speaking of food,' somewhere in your response and mention a random dish. If it mentions food, just answer normally.",
                    "verifier": "food_tangent_if_no_food",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "How do airplanes stay in the air?",
                        "What is the stock market?",
                        "Explain how batteries work.",
                    ],
                    "non_trigger_inputs": [
                        "What's the best way to cook pasta?",
                        "Is chocolate good for your health?",
                        "How do you make sourdough bread?",
                    ],
                },
                {
                    "instruction": "If the user's message does NOT contain the word 'please', start your response with 'Remember to say please! ' and then answer. If 'please' is present, just answer directly.",
                    "verifier": "please_reminder_if_no_please",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Tell me how to bake a cake.",
                        "What's the weather like on Mars?",
                        "Explain gravity to me.",
                    ],
                    "non_trigger_inputs": [
                        "Please tell me how to bake a cake.",
                        "Could you please explain the weather on Mars?",
                        "Please explain gravity to me.",
                    ],
                },
            ],
        },
        # Type 6: Nested-conditional
        {
            "type": "nested",
            "description": "If condition A, then check condition B for further branching",
            "instructions": [
                {
                    "instruction": "If the user asks about a beverage: if it's a hot beverage (coffee, tea, hot chocolate), describe it warmly and end with 'Enjoy it warm!'; if it's a cold beverage (juice, soda, smoothie), end with 'Best served chilled!'. If not about a beverage, respond normally.",
                    "verifier": "nested_beverage",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Tell me about coffee.",
                        "What are the benefits of green tea?",
                        "How is orange juice made?",
                    ],
                    "non_trigger_inputs": [
                        "Tell me about volcanoes.",
                        "How does a car engine work?",
                        "What is photosynthesis?",
                    ],
                },
                {
                    "instruction": "If the user's message contains a number: if the number is even, write your response in exactly 2 paragraphs; if the number is odd, write your response in exactly 3 paragraphs. If no number, write a single paragraph.",
                    "verifier": "nested_number_parity",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "Tell me 4 facts about space.",
                        "I have 7 books to read this month.",
                        "What happened in the year 2000?",
                    ],
                    "non_trigger_inputs": [
                        "Tell me about space exploration.",
                        "I have many books to read.",
                        "What happened in recent history?",
                    ],
                },
            ],
        },
        # Type 7: Multi-condition AND
        {
            "type": "multi_and",
            "description": "Both conditions must be met for the action to trigger",
            "instructions": [
                {
                    "instruction": "If the user's message contains BOTH a question mark AND the word 'why', begin your answer with 'Great question! ' (exactly). Otherwise, respond normally.",
                    "verifier": "prefix_if_both_conditions",
                    "verifier_args": {"conditions": ["?", "why"], "prefix": "Great question! "},
                    "trigger_inputs": [
                        "Why is the sky blue?",
                        "Why do cats purr?",
                        "Why does ice float on water?",
                    ],
                    "non_trigger_inputs": [
                        "Explain why the sky is blue.",  # no question mark
                        "What color is the sky?",  # no 'why'
                        "Tell me about the sky.",  # neither
                    ],
                },
                {
                    "instruction": "If the user's message mentions BOTH a season (spring, summer, fall/autumn, winter) AND a sport, include a recommendation for watching that sport in that season. Otherwise, just answer the question.",
                    "verifier": "season_sport_recommendation",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "What's the best way to enjoy soccer in the summer?",
                        "Tell me about skiing in winter.",
                        "Is tennis popular in the spring?",
                    ],
                    "non_trigger_inputs": [
                        "What's the best way to enjoy summer?",  # no sport
                        "Tell me about soccer.",  # no season
                        "What's the weather like today?",  # neither
                    ],
                },
            ],
        },
        # Type 8: Multi-condition OR
        {
            "type": "multi_or",
            "description": "Either condition triggers the action",
            "instructions": [
                {
                    "instruction": "If the user's message contains either the word 'help' or the word 'assist', begin your response with 'I\\'m here to help! ' (exactly). Otherwise, respond normally.",
                    "verifier": "prefix_if_either_keyword",
                    "verifier_args": {"keywords": ["help", "assist"], "prefix": "I'm here to help! "},
                    "trigger_inputs": [
                        "Can you help me understand quantum physics?",
                        "I need someone to assist me with my homework.",
                        "Please help me fix this code.",
                    ],
                    "non_trigger_inputs": [
                        "Explain quantum physics to me.",
                        "I'm working on my homework.",
                        "What is wrong with this code?",
                    ],
                },
                {
                    "instruction": "If the user mentions either 'morning' or 'evening', include the current-context appropriate greeting ('Good morning!' or 'Good evening!') at the start of your response. Otherwise, respond without a time-based greeting.",
                    "verifier": "greeting_if_time_of_day",
                    "verifier_args": {},
                    "trigger_inputs": [
                        "I always exercise in the morning.",
                        "What's a good evening routine?",
                        "The morning light is beautiful today.",
                    ],
                    "non_trigger_inputs": [
                        "I always exercise regularly.",
                        "What's a good daily routine?",
                        "The sunlight is beautiful today.",
                    ],
                },
            ],
        },
    ]


def build_scaling_benchmark():
    """Build test cases with 1, 2, and 4 simultaneous conditions."""
    conditions = [
        {
            "instruction": "If the message contains the word 'science', include '[SCI]' somewhere in your response.",
            "keyword": "science",
            "marker": "[SCI]",
        },
        {
            "instruction": "If the message contains the word 'history', include '[HIST]' somewhere in your response.",
            "keyword": "history",
            "marker": "[HIST]",
        },
        {
            "instruction": "If the message contains the word 'art', include '[ART]' somewhere in your response.",
            "keyword": "art",
            "marker": "[ART]",
        },
        {
            "instruction": "If the message contains the word 'math', include '[MATH]' somewhere in your response.",
            "keyword": "math",
            "marker": "[MATH]",
        },
    ]

    test_cases = []

    # 1-condition tests
    for i, cond in enumerate(conditions):
        combined_instruction = cond["instruction"]
        # Trigger input
        test_cases.append({
            "id": f"scale_1cond_{i}_trigger",
            "type": "scaling_1",
            "num_conditions": 1,
            "instruction": combined_instruction,
            "input": f"Tell me about {cond['keyword']} and its impact on society.",
            "expected_markers": [cond["marker"]],
            "absent_markers": [],
            "should_trigger": True,
        })
        # Non-trigger
        test_cases.append({
            "id": f"scale_1cond_{i}_nontrigger",
            "type": "scaling_1",
            "num_conditions": 1,
            "instruction": combined_instruction,
            "input": "Tell me about the weather today.",
            "expected_markers": [],
            "absent_markers": [cond["marker"]],
            "should_trigger": False,
        })

    # 2-condition tests
    pairs = [(0,1), (2,3), (0,2), (1,3)]
    for pi, (a, b) in enumerate(pairs):
        combined = conditions[a]["instruction"] + " " + conditions[b]["instruction"]
        # Both trigger
        test_cases.append({
            "id": f"scale_2cond_{pi}_both_trigger",
            "type": "scaling_2",
            "num_conditions": 2,
            "instruction": combined,
            "input": f"I love both {conditions[a]['keyword']} and {conditions[b]['keyword']}.",
            "expected_markers": [conditions[a]["marker"], conditions[b]["marker"]],
            "absent_markers": [],
            "should_trigger": True,
        })
        # One trigger
        test_cases.append({
            "id": f"scale_2cond_{pi}_one_trigger",
            "type": "scaling_2",
            "num_conditions": 2,
            "instruction": combined,
            "input": f"Tell me about {conditions[a]['keyword']} please.",
            "expected_markers": [conditions[a]["marker"]],
            "absent_markers": [conditions[b]["marker"]],
            "should_trigger": True,  # partial
        })
        # None trigger
        test_cases.append({
            "id": f"scale_2cond_{pi}_none_trigger",
            "type": "scaling_2",
            "num_conditions": 2,
            "instruction": combined,
            "input": "Tell me about the weather today.",
            "expected_markers": [],
            "absent_markers": [conditions[a]["marker"], conditions[b]["marker"]],
            "should_trigger": False,
        })

    # 4-condition tests
    combined_all = " ".join(c["instruction"] for c in conditions)
    all_markers = [c["marker"] for c in conditions]
    all_keywords = [c["keyword"] for c in conditions]

    # All trigger
    test_cases.append({
        "id": "scale_4cond_all_trigger",
        "type": "scaling_4",
        "num_conditions": 4,
        "instruction": combined_all,
        "input": f"I'm interested in {', '.join(all_keywords[:3])}, and {all_keywords[3]}.",
        "expected_markers": all_markers,
        "absent_markers": [],
        "should_trigger": True,
    })
    # Two trigger
    test_cases.append({
        "id": "scale_4cond_two_trigger",
        "type": "scaling_4",
        "num_conditions": 4,
        "instruction": combined_all,
        "input": f"I study {all_keywords[0]} and {all_keywords[2]}.",
        "expected_markers": [all_markers[0], all_markers[2]],
        "absent_markers": [all_markers[1], all_markers[3]],
        "should_trigger": True,
    })
    # None trigger
    test_cases.append({
        "id": "scale_4cond_none_trigger",
        "type": "scaling_4",
        "num_conditions": 4,
        "instruction": combined_all,
        "input": "Tell me about cooking Italian food.",
        "expected_markers": [],
        "absent_markers": all_markers,
        "should_trigger": False,
    })

    return test_cases


if __name__ == "__main__":
    cases = build_benchmark()
    print(f"Total test cases: {len(cases)}")
    type_counts = {}
    for c in cases:
        type_counts[c["type"]] = type_counts.get(c["type"], 0) + 1
    for t, count in sorted(type_counts.items()):
        print(f"  {t}: {count}")

    scaling = build_scaling_benchmark()
    print(f"\nScaling test cases: {len(scaling)}")

    # Save
    with open("results/benchmark.json", "w") as f:
        json.dump(cases, f, indent=2)
    with open("results/scaling_benchmark.json", "w") as f:
        json.dump(scaling, f, indent=2)
    print("Saved to results/")
