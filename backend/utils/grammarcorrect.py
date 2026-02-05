import yt_dlp
import argparse
import os
import glob
import requests
import re

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

    vtt_files = glob.glob("temp*.vtt")
    if not vtt_files:
        print("No transcript available for this video.")
        return

    with open(vtt_files[0], "r", encoding="utf-8") as f:
        vtt = f.read()

    os.remove(vtt_files[0])

    text = vtt_to_text(vtt)
    text = grammar_correct(text)

    with open(output + ".txt", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Transcript saved to {output}.txt")

def vtt_to_text(vtt):
    lines = vtt.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or "-->" in line or line.startswith("WEBVTT"):
            continue
        cleaned.append(line)

    text = re.sub(r"\s+", " ", " ".join(cleaned))
    sentences = re.split(r"(?<=[.!?]) +", text)
    paragraphs = [" ".join(sentences[i:i+4]) for i in range(0, len(sentences), 4)]
    return "\n\n".join(paragraphs)

def grammar_correct(text):
    chunks = chunk_text(text, 500)
    corrected = []

    for chunk in chunks:
        r = requests.post(
            "https://api.languagetool.org/v2/check",
            data={"text": chunk, "language": "en-US"},
            timeout=30
        )
        data = r.json()
        matches = data.get("matches", [])

        offset = 0
        for match in matches:
            if not match["replacements"]:
                continue
            start = match["offset"] + offset
            length = match["length"]
            replacement = match["replacements"][0]["value"]
            chunk = chunk[:start] + replacement + chunk[start+length:]
            offset += len(replacement) - length

        corrected.append(chunk)

    return "\n\n".join(corrected)

def chunk_text(text, size):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

def main():
    parser = argparse.ArgumentParser(description="Download YouTube video, audio, or transcript")
    parser.add_argument("url")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-v", action="store_true", help="Download video")
    group.add_argument("-a", action="store_true", help="Download audio")
    group.add_argument("-t", action="store_true", help="Download transcript")
    parser.add_argument("-o", "--output", default="output", help="Output filename without extension")
    args = parser.parse_args()

    if args.v:
        download_video(args.url, args.output)
    elif args.a:
        download_audio(args.url, args.output)
    elif args.t:
        download_transcript(args.url, args.output)

if __name__ == "__main__":
    main()
