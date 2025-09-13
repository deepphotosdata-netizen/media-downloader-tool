#!/usr/bin/env python3
"""
Media Downloader Tool
Downloads and converts .m3u8 files to .mkv, downloads PDFs, and handles YouTube links
"""

import os
import sys
import re
import requests
import subprocess
import ffmpeg
import yt_dlp
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional


class MediaDownloader:
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def read_urls_from_file(self, file_path: str) -> List[Dict[str, str]]:
        """Read URLs from a .txt file, extracting URLs and titles from lines"""
        try:
            entries = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Extract URL from line (handles format: "Title: https://...")
                    url_match = re.search(r'https?://[^\s]+', line)
                    if url_match:
                        url = url_match.group()
                        # Extract title (everything before the URL)
                        title = line[:url_match.start()].strip().rstrip(':')
                        if not title:
                            title = "Untitled"
                        entries.append({'url': url, 'title': title})
                    elif line.startswith('http'):
                        # Line starts with URL directly
                        entries.append({'url': line, 'title': "Untitled"})
                    else:
                        print(f"Warning: No URL found in line {line_num}: {line[:50]}...")
            
            print(f"Found {len(entries)} URLs in {file_path}")
            return entries
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    
    def get_filename_from_url(self, url: str, title: str = "", extension: Optional[str] = None) -> Path:
        """Generate filename path based on URL structure and title: domain/title.extension"""
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path.lstrip('/')
        
        # Remove query parameters and fragments
        if '?' in path:
            path = path.split('?')[0]
        if '#' in path:
            path = path.split('#')[0]
            
        # If path is empty, use a default filename
        if not path:
            path = "download"
            
        # Sanitize domain and path separately (preserve / for directory structure)
        safe_domain = re.sub(r'[<>:"|?*]', '_', domain)
        safe_path = re.sub(r'[<>:"|?*]', '_', path)
        
        # Remove path traversal segments for security
        path_parts = [part for part in safe_path.split('/') if part and part != '..' and part != '.']
        safe_path = '/'.join(path_parts) if path_parts else 'download'
        
        # Use title for filename if available, otherwise use path
        if title:
            # Sanitize title for filename
            safe_title = re.sub(r'[<>:"|?*\\]', '_', title)
            safe_title = re.sub(r'[/]', '-', safe_title)  # Replace / with -
            rel_path = Path(safe_domain) / f"{safe_title}.temp"
        else:
            rel_path = Path(safe_domain) / safe_path
        
        if extension:
            # Use pathlib to safely change extension
            rel_path = rel_path.with_suffix(extension)
            
        return rel_path
    
    def is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube video"""
        youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)',
            r'youtube\.com/.*[?&]v=',
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)
    
    def download_youtube_video(self, url: str, title: str = "") -> bool:
        """Download YouTube video at 480p quality using yt-dlp"""
        try:
            rel_path = self.get_filename_from_url(url, title)
            output_path = self.output_dir / rel_path
            
            # Create directory structure
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            ydl_opts = {
                'format': 'bv*[height<=480]+ba/b[height<=480]',  # Better format selection for 480p with audio
                'outtmpl': str(output_path / '%(title)s.%(ext)s'),
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading YouTube video: {url}")
                ydl.download([url])
                print(f"Successfully downloaded to: {rel_path}")
                return True
                
        except Exception as e:
            print(f"Error downloading YouTube video {url}: {e}")
            return False
    
    def download_pdf(self, url: str, title: str = "") -> bool:
        """Download PDF file directly"""
        try:
            rel_path = self.get_filename_from_url(url, title, '.pdf')
            output_path = self.output_dir / rel_path
            
            # Create directory structure
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Downloading PDF: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    
            print(f"Successfully downloaded: {rel_path}")
            return True
            
        except Exception as e:
            print(f"Error downloading PDF {url}: {e}")
            return False
    
    def download_m3u8_and_convert(self, url: str, title: str = "") -> bool:
        """Download .m3u8 file and convert to .mkv at 480p"""
        try:
            rel_path = self.get_filename_from_url(url, title, '.mkv')
            output_path = self.output_dir / rel_path
            
            # Create directory structure
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Downloading and converting M3U8: {url}")
            
            # Use ffmpeg to download and convert m3u8 to mkv
            try:
                (
                    ffmpeg
                    .input(url)
                    .output(str(output_path), 
                           vcodec='libx264',
                           acodec='aac',
                           vf='scale=-2:480',  # Scale to 480p height, maintain aspect ratio
                           format='matroska')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                print(f"Successfully converted to: {rel_path}")
                return True
                
            except ffmpeg.Error as e:
                print(f"FFmpeg error: {e.stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"Error processing M3U8 {url}: {e}")
            return False
    
    def process_urls(self, txt_file_path: str) -> Dict[str, int]:
        """Process all URLs from the text file"""
        entries = self.read_urls_from_file(txt_file_path)
        if not entries:
            return {"total": 0, "success": 0, "failed": 0}
        
        stats = {"total": len(entries), "success": 0, "failed": 0}
        
        for i, entry in enumerate(entries, 1):
            url = entry['url']
            title = entry['title']
            print(f"\nProcessing {i}/{len(entries)}: {title}")
            print(f"URL: {url}")
            
            try:
                if self.is_youtube_url(url):
                    success = self.download_youtube_video(url, title)
                elif url.lower().endswith('.pdf'):
                    success = self.download_pdf(url, title)
                elif '.m3u8' in url.lower():
                    success = self.download_m3u8_and_convert(url, title)
                else:
                    print(f"Unsupported URL type: {url}")
                    success = False
                
                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                    
            except Exception as e:
                print(f"Unexpected error processing {url}: {e}")
                stats["failed"] += 1
        
        return stats


def main():
    print("Media Downloader Tool")
    print("====================")
    
    # Get input file path
    if len(sys.argv) > 1:
        txt_file = sys.argv[1]
    else:
        txt_file = input("Enter the path to your .txt file containing URLs: ").strip()
    
    if not txt_file:
        print("No file provided. Exiting.")
        return
    
    # Initialize downloader
    downloader = MediaDownloader()
    
    # Process URLs
    print(f"\nStarting download process...")
    print(f"Output directory: {downloader.output_dir.absolute()}")
    
    stats = downloader.process_urls(txt_file)
    
    # Print summary
    print(f"\n{'='*50}")
    print("DOWNLOAD SUMMARY")
    print(f"{'='*50}")
    print(f"Total URLs processed: {stats['total']}")
    print(f"Successful downloads: {stats['success']}")
    print(f"Failed downloads: {stats['failed']}")
    print(f"Output directory: {downloader.output_dir.absolute()}")
    
    if stats['failed'] > 0:
        print(f"\nNote: {stats['failed']} downloads failed. Check the output above for details.")


if __name__ == "__main__":
    main()