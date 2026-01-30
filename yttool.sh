#!/bin/bash

figlet yttool 2>/dev/null || echo "yttool"

echo "yttool: quickly download YouTube videos, audio, or captions"
echo

read -p "URL: " url
read -p "Output filename (without extension, leave blank for default): " filename

echo "1. Download video"
echo "2. Download audio"
echo "3. Download transcript"
echo "4. Download transcript without timestamp"
echo "5. Quit"

read -p "What do you want to do: " choice

case $choice in
1)
  if [ -z "$filename" ]; then
    yt-dlp "$url"
  else
    yt-dlp -o "${filename}.%(ext)s" "$url"
  fi
  ;;
2)
  if [ -z "$filename" ]; then
    yt-dlp -x --audio-format mp3 "$url"
  else
    yt-dlp -x --audio-format mp3 -o "${filename}.%(ext)s" "$url"
  fi
  ;;
3)
  if [ -z "$filename" ]; then
    yt-dlp --write-subs --write-auto-sub --sub-format "vtt" --skip-download "$url"
  else
    yt-dlp --write-subs --write-auto-sub --sub-format "vtt" --skip-download -o "${filename}.%(ext)s" "$url"
  fi
  ;;
4)
  if [ -z "$filename" ]; then
    yt-dlp --write-subs --write-auto-sub --sub-format "plain" --skip-download "$url"
  else
    yt-dlp --write-subs --write-auto-sub --sub-format "plain" --skip-download -o "${filename}.%(ext)s" "$url"
  fi
  ;;
5)
  echo "Goodbye"
  exit 0
  ;;
*)
  echo "Invalid option"
  ;;
esac
