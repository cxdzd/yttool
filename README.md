# yttool

> Website in development

yttool is a simple command-line tool to download YouTube videos, audio, or transcripts. You can also set custom filenames for your downloads.

## Features

- Download full videos
- Extract audio only (MP3 format)
- Download transcripts (with or without timestamps)
- Option to set custom output filenames

## Requirements

- Bash (Linux, macOS, or WSL on Windows)
- yt-dlp
- figlet (optional)

### Installing Dependencies

**On Ubuntu/Debian:**

sudo apt update
sudo apt install yt-dlp figlet

**On macOS (with Homebrew):**

brew install yt-dlp figlet

**On Windows:**

- Install WSL and follow the Linux instructions, or
- Download /dist/yt-dlp.exe and place it in a folder in your PATH, or get it from releases.

One liner that does everythin for you lazy people
`git clone https://github.com/cxdzd/yttool.git && cd yttool && chmod +x yttool.sh && sudo apt update && sudo apt install -y yt-dlp figlet && ./yttool.sh`

## Usage

1. Make the script executable:

chmod +x yttool.sh

2. Run the script:

./yttool.sh

3. Follow the prompts:

- Enter the YouTube URL
- Optionally enter a filename for your download
- Choose an action from the menu (video, audio, transcript, etc.)

## Example

```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Output filename: rickroll
1. Download video
2. Download audio
3. Download transcript
4. Download transcript without timestamp
5. Quit
What do you want to do: 2
```

This will download the audio as rickroll.mp3.

## Notes

- If you leave the filename blank, yt-dlp will use the default video title.
- Not all videos have transcripts available.
- Ensure you comply with YouTube’s terms of service when downloading content.
