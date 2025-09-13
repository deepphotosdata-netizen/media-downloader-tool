# Media Downloader Tool

## Overview

This is a Python-based media downloader tool designed to handle multiple types of media content. The application downloads and converts M3U8 video streams to MKV format, downloads PDF documents, and processes YouTube links. It supports batch processing by reading URLs from text files and organizes downloads in a structured directory format.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**Single-File Architecture**: The application follows a monolithic design with all functionality contained in `media_downloader.py`. This approach simplifies deployment and maintenance for a focused utility tool.

**MediaDownloader Class**: Serves as the main controller, encapsulating all download logic and file management operations. This object-oriented approach provides clean separation of concerns and easy extensibility.

**File-Based Input System**: Uses text files (`sample_urls.txt`) for batch URL processing, allowing users to prepare download lists offline and process them systematically.

### Media Processing Pipeline

**Multi-Format Support**: Handles three distinct media types (M3U8 streams, PDFs, YouTube videos) through specialized processing methods, providing flexibility for various content sources.

**URL-Based File Organization**: Implements intelligent filename generation based on URL structure (domain/path.extension), creating organized output directories that mirror source locations.

**Stream Conversion**: Utilizes FFmpeg for M3U8 to MKV conversion, ensuring compatibility and quality retention for video content.

### Error Handling Strategy

**Graceful Degradation**: Implements comprehensive error handling for file operations, network requests, and media processing to ensure batch operations continue despite individual failures.

**User Feedback**: Provides clear console output for operation status, error reporting, and progress tracking.

## External Dependencies

### Media Processing Libraries
- **ffmpeg-python**: Handles video stream conversion and processing
- **yt-dlp**: YouTube and video platform downloading capabilities
- **requests**: HTTP operations for direct file downloads

### System Requirements
- **FFmpeg**: External binary requirement for video processing
- **Python 3.x**: Runtime environment with pathlib, urllib, and typing support

### File System Dependencies
- Local file system access for downloads directory creation
- Text file reading capabilities for URL input processing
- Cross-platform path handling through pathlib