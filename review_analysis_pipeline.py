import json
import os
from pathlib import Path
from llm_review_client import parse_review_line_to_json

REVIEW_FILE_PATH = "app_reviews.txt"
LEGACY_REVIEW_FILE_PATH = "app_reviews.txt"
JOIN_SEPARATOR = "#####"

def load_review_lines(file_path):
    if not Path(file_path).exists() and Path(LEGACY_REVIEW_FILE_PATH).exists():
        file_path = LEGACY_REVIEW_FILE_PATH

    review_lines = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            review_lines.append(line.strip())
    return review_lines

def build_reviews_json(review_lines):
    reviews_json = []
    for review_line in review_lines:
        review_json = parse_review_line_to_json(review_line)
        review_dict = json.loads(review_json)
        reviews_json.append(review_dict)
    return reviews_json

def count_and_join_reviews(review_dicts):
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    review_dict_strings = []

    for review_dict in review_dicts:
        sentiment = review_dict.get("avaliacao", "Neutra")
        if sentiment == "Positiva":
            positive_count += 1
        elif sentiment == "Negativa":
            negative_count += 1
        else:
            neutral_count += 1

        review_dict_strings.append(json.dumps(review_dict, ensure_ascii=False))

    joined_text = JOIN_SEPARATOR.join(review_dict_strings)
    return positive_count, negative_count, neutral_count, joined_text

def main():
    llm_mode = os.getenv("LLM_MODE", "local").strip().lower()
    print(f"LLM mode: {llm_mode}\n")

    review_lines = load_review_lines(REVIEW_FILE_PATH)
    reviews_json = build_reviews_json(review_lines)
    positives, negatives, neutrals, joined_reviews = count_and_join_reviews(reviews_json)

    print(f"Positivas: {positives}\n")
    print(f"Negativas: {negatives}\n")
    print(f"Neutras: {neutrals}\n")
    print(joined_reviews)

if __name__ == "__main__":
    main()