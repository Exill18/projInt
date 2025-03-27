import os
import argparse
import logging
import subprocess
from pathlib import Path
import math


# Configure paths
BASE_DIR = Path(__file__).parent
FFMPEG_DIR = BASE_DIR / "ffmpeg"
FFMPEG_PATH = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_PATH = FFMPEG_DIR / "ffprobe.exe"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ffmpeg():
    if not FFMPEG_PATH.exists() or not FFPROBE_PATH.exists():
        raise FileNotFoundError(
            "FFmpeg binaries not found. Please download from:\n"
            "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip\n"
            "and extract to 'ffmpeg' directory"
        )

def get_video_files(input_dir):
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
    return [f for f in Path(input_dir).iterdir() if f.suffix.lower() in video_extensions]

def get_video_metadata(input_file):
    cmd = [
        str(FFPROBE_PATH),
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=duration,bit_rate",
        "-of", "csv=p=0",
        str(input_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    duration, bitrate = map(float, result.stdout.strip().split(","))
    return duration, bitrate

def calculate_segments(duration, bitrate, target_size_mb=9.9):
    file_size_bytes = (bitrate * duration) / 8
    target_bytes = target_size_mb * 1024 * 1024
    num_segments = math.ceil(file_size_bytes / target_bytes)
    segment_duration = duration / num_segments
    return num_segments, segment_duration

def split_video(input_file, output_dir):
    duration, bitrate = get_video_metadata(input_file)
    num_segments, seg_duration = calculate_segments(duration, bitrate)
    
    output_pattern = output_dir / f"{input_file.stem}_part_%03d{input_file.suffix}"
    
    cmd = [
        str(FFMPEG_PATH),
        "-i", str(input_file),
        "-c", "copy",
        "-f", "segment",
        "-segment_time", str(seg_duration),
        "-reset_timestamps", "1",
        "-force_key_frames", f"expr:gte(n,n_forced*{seg_duration})",
        str(output_pattern)
    ]
    
    subprocess.run(cmd, check=True)
    return list(output_dir.glob(output_pattern.name.replace("%03d", "*")))

def run_bot():
    """Run the Discord bot to upload the split videos"""
    try:
        result = subprocess.run(["python", "bot.py"], check=True, capture_output=True, text=True)
        logging.info(f"Bot output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running bot: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error running bot: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Split videos into ~10MB segments')
    parser.add_argument('input_dir', help='Input directory containing videos')
    parser.add_argument('--output-dir', default='split_videos', help='Output directory')
    args = parser.parse_args()

    try:
        check_ffmpeg()
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_dir.mkdir(exist_ok=True)
        video_files = get_video_files(input_dir)
        
        if not video_files:
            logging.warning("No video files found in input directory")
            return
        
        for video_file in video_files:
            try:
                parts = split_video(video_file, output_dir)
                logging.info(f"Created {len(parts)} parts for {video_file.name}")
            except Exception as e:
                logging.error(f"Failed to process {video_file.name}: {str(e)}")

        run_bot()
                
    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()