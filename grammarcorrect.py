import argparse
import os
import sys
import re
import language_tool_python

CHUNK_SIZE = 500

def chunk_text(text, size):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i + size])

def normalize(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def format_paragraphs(text):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    paragraphs = []
    current = []

    for s in sentences:
        current.append(s)
        if len(" ".join(current).split()) >= 80:
            paragraphs.append(" ".join(current))
            current = []

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output")
    parser.add_argument("--lang", default="en-US")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    tool = language_tool_python.LanguageTool(args.lang)

    fixed = []
    for chunk in chunk_text(text, CHUNK_SIZE):
        fixed.append(tool.correct(chunk))

    result = " ".join(fixed)
    result = normalize(result)
    result = format_paragraphs(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        print(result)

if __name__ == "__main__":
    main()