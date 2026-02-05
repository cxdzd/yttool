#!/usr/bin/env python3
import yt_dlp
import argparse
import glob
from pathlib import Path
import re
import requests
from charset_normalizer import from_path

def download_video(url, output):
    ydl_opts = {
        "format": "best",
        "outtmpl": output + ".mp4"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_audio(url, output):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output + ".mp3",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def detect_encoding(file_path):
    res = from_path(file_path).best()
    encoding = res.encoding
    if res.bom and encoding == "utf_8":
        encoding += "_sig"
    return encoding

def read_subtitle(file_path, encoding=None):
    encoding = encoding or detect_encoding(file_path)
    with open(file_path, "r", encoding=encoding) as f:
        return [line.strip() for line in f]

def remove_junk(lines, remove_names=True):
    cleaned = []
    junk_patterns = [r"<.*?>", r"\{.*?\}", r"\[.*?\]", r"\(.*?\)", r"^-\s"]
    name_pattern = r"^.*?:"
    for line in lines:
        if not line:
            continue
        if re.match(r"(\d{2}:)?\d{2}:\d{2}\.\d{3} --> (\d{2}:)?\d{2}:\d{2}\.\d{3}", line):
            continue
        if line.isdigit() or line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        for pattern in junk_patterns:
            line = re.sub(pattern, "", line)
        if remove_names:
            line = re.sub(name_pattern, "", line)
        line = line.strip()
        if line:
            cleaned.append(line)
    return cleaned

def join_lines_to_paragraphs(lines, sentences_per_paragraph=4):
    text = " ".join(lines)
    sentences = re.split(r"(?<=[.!?]) +", text)
    paragraphs = [" ".join(sentences[i:i+sentences_per_paragraph])
                  for i in range(0, len(sentences), sentences_per_paragraph)]
    return "\n\n".join(paragraphs)

def subtitles_to_text(file_path):
    lines = read_subtitle(file_path)
    lines = remove_junk(lines)
    return join_lines_to_paragraphs(lines)

def grammar_correct(text):
    chunks = [text.split()[i:i+500] for i in range(0, len(text.split()), 500)]
    corrected = []
    for chunk in chunks:
        chunk_text = " ".join(chunk)
        r = requests.post("https://api.languagetool.org/v2/check",
                          data={"text": chunk_text, "language": "en-US"},
                          timeout=30)
        data = r.json()
        matches = data.get("matches", [])
        offset = 0
        for match in matches:
            if not match["replacements"]:
                continue
            start = match["offset"] + offset
            length = match["length"]
            replacement = match["replacements"][0]["value"]
            chunk_text = chunk_text[:start] + replacement + chunk_text[start+length:]
            offset += len(replacement) - length
        corrected.append(chunk_text)
    return "\n\n".join(corrected)

def download_transcript(url, output):
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "vtt",
        "subtitleslangs": ["en"],
        "outtmpl": "temp"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)
    vtt_files = glob.glob("temp*.vtt*")
    if not vtt_files:
        print("No transcript available for this video.")
        return
    vtt_path = vtt_files[0]
    text = subtitles_to_text(vtt_path)
    text = grammar_correct(text)
    Path(vtt_path).unlink()
    Path(output + ".txt").write_text(text, encoding="utf-8")
    print(f"Transcript saved to {output}.txt")

def main():
    parser = argparse.ArgumentParser(description="Download YouTube video, audio, or transcript")
    parser.add_argument("url")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-v", action="store_true")
    group.add_argument("-a", action="store_true")
    group.add_argument("-t", action="store_true")
    parser.add_argument("-o", "--output", default="output")
    args = parser.parse_args()
    if args.v:
        download_video(args.url, args.output)
    elif args.a:
        download_audio(args.url, args.output)
    elif args.t:
        download_transcript(args.url, args.output)

if __name__ == "__main__":
    main()
