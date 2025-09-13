# Media Downloader Tool

A Python-based media downloader tool designed to handle multiple types of media content.

## Features

- Downloads and converts M3U8 video streams to MKV format
- Downloads PDF documents
- Processes YouTube links
- Supports batch processing from text files
- Organized directory structure for downloads

## Dependencies

- Python 3.11+
- ffmpeg-python
- requests
- yt-dlp
- FFmpeg (system dependency)

## Installation

```bash
pip install ffmpeg-python requests yt-dlp
```

## Usage

1. Create a text file with URLs (one per line)
2. Run the media downloader:
   ```bash
   python media_downloader.py
   ```

## Project Structure

- `media_downloader.py` - Main application file
- `pyproject.toml` - Project dependencies and metadata
- `sample_urls.txt` - Example URLs for testing
- `downloads/` - Output directory for downloaded media
