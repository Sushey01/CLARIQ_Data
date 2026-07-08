"""Generate an expanded Socratic fine-tuning dataset for Grade 10 science tutoring."""

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "socratic_finetuning_data.jsonl"
EXPANDED_PATH = ROOT / "socratic_finetuning_data.expanded.jsonl"

# Topics drawn from the current dataset and the Grade 10 curriculum contents.
TOPICS = [
    "Acids, Bases and Salts",
    "Carbon and its Compounds",
    "Chemical Reactions and Equations",
    "Control and Coordination",
    "Electricity",
    "Electricity and Magnetism",
    "General Concept",
    "Heredity and Evolution",
    "How do Organisms Reproduce?",
    "Hydrocarbon and its Compounds",
    "Life Processes",
    "Light Reflection and Refraction",
    "Magnetic Effects of Electric Current",
    "Metal and Not metals",
    "Motion and Force",
    "Nature and Environment",
    "Our Environment",
    "Pressure",
    "The Human Eye and the Colourful World",
    "Universe",
    "Vision Defects",
    "Wave",
    "Classification of Living Beings",
    "Physiological Structure and Life Process",
    "Classification of Elements",
    "Gases",
    "Chemicals used in Daily Life",
    "Information and Communication Technology",
    "Honey Bee",
    "Scientific Learning",
]

INPUT_TEMPLATES = [
    "Can you explain how {topic} works?",
    "How does {topic} relate to real-world applications?",
    "What are the main characteristics of {topic}?",
    "Can you give me an example of {topic}?",
    "Why is {topic} important to learn?",
    "Why does {topic} occur?",
    "Is there a formula or rule that governs {topic}?",
    "How do scientists measure or observe {topic}?",
    "What is the fundamental principle behind {topic}?",
    "Compare {topic} with related concepts",
    "Describe {topic} in detail",
    "Explain what {topic} means",
    "How would you apply {topic} in real life?",
    "What happens if we change the conditions for {topic}?",
    "What is the key idea behind {topic}?",
]

OUTPUT_TEMPLATES = [
    "Interesting perspective on {topic}. Let's test that hypothesis. If your assumption is correct, what other phenomena should also follow the same pattern?",
    "Good question! Understanding {topic} is crucial. What is the main difference between this idea and what we learned last week?",
    "That is one of the most important questions in science regarding {topic}. What evidence or observation could help us decide between the options?",
    "That's a very insightful question about {topic}. What fits the evidence better: idea A or idea B, and why?",
    "I'm glad you're curious about {topic}. If you had to explain this to a younger student, what analogy would you use?",
    "Let's tackle {topic} using the Socratic method. What do you already know for sure, and what are the 'unknowns' we need to sort out?",
    "I love that you're asking about {topic}. Instead of giving the answer directly, what question should we ask next to clarify the key concept?",
    "You're on the right track with {topic}. Can you recall a similar concept from earlier, and how might that help here?",
    "Excellent thought process! If we change one condition in this {topic} scenario, how would that affect the result?",
    "That's a great question about {topic}! Before answering, what observation would you expect if the strongest explanation is true?",
    "Interesting perspective on {topic}. If this were true, what would we see in a real experiment?",
    "Good question! Think about the most basic property of {topic}. How does that property guide what happens next?",
]


def load_existing_dataset(path: Path) -> list[dict]:
    if not path.exists():
        return []

    examples = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            examples.append(json.loads(line))
    return examples


def generate_new_examples(existing: list[dict], target_multiple: int = 10) -> list[dict]:
    existing_set = {(item["instruction"], item["input"], item["output"]) for item in existing}
    output = list(existing)
    target_count = max(len(existing) * target_multiple, len(existing))

    random.seed(42)
    attempts = 0
    while len(output) < target_count and attempts < 20000:
        topic = random.choice(TOPICS)
        input_text = random.choice(INPUT_TEMPLATES).format(topic=topic)
        output_text = random.choice(OUTPUT_TEMPLATES).format(topic=topic)
        instruction = f"You are a Socratic tutor teaching a Grade 10 student about {topic}."
        if (instruction, input_text, output_text) in existing_set:
            attempts += 1
            continue

        example = {
            "instruction": instruction,
            "input": input_text,
            "output": output_text,
        }
        output.append(example)
        existing_set.add((instruction, input_text, output_text))

    if len(output) < target_count:
        raise RuntimeError(
            f"Could not generate enough unique examples after {attempts} attempts"
        )

    return output


def write_dataset(path: Path, examples: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for item in examples:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expand Socratic fine-tuning data.")
    parser.add_argument(
        "--output",
        type=Path,
        default=EXPANDED_PATH,
        help="Output JSONL file path",
    )
    parser.add_argument(
        "--target-multiple",
        type=int,
        default=10,
        help="Target dataset size multiplier relative to the existing dataset",
    )
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="Include the existing dataset examples in the output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    existing = load_existing_dataset(DATA_PATH)
    if not existing:
        print(f"No existing dataset found at {DATA_PATH}. Starting from scratch.")

    expanded = generate_new_examples(existing, target_multiple=args.target_multiple)
    write_dataset(args.output, expanded)
    print(f"Wrote {len(expanded)} Socratic examples to {args.output}")


if __name__ == "__main__":
    main()
