import os
import argparse
import logging
import subprocess
from pathlib import Path
import math
import zipfile

# Configure paths
BASE_DIR = Path(__file__).parent
FFMPEG_DIR = BASE_DIR / "ffmpeg"
FFMPEG_PATH = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_PATH = FFMPEG_DIR / "ffprobe.exe"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_zip_files(input_dir, temp_dir):
    """Extract all ZIP files in the input directory to a temporary directory."""
    for zip_file in Path(input_dir).glob('*.zip'):
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                logging.info(f"Extracted {zip_file} to {temp_dir}")
        except Exception as e:
            logging.error(f"Failed to extract {zip_file}: {str(e)}")

def get_media_files(input_dir):
    """Get all video and image files from the input directory."""
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    media_extensions = video_extensions + image_extensions

    return [f for f in Path(input_dir).rglob('*') if f.suffix.lower() in media_extensions]

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
    parser = argparse.ArgumentParser(description='Split videos and process media files.')
    parser.add_argument('input_dir', help='Input directory containing videos, images, or ZIP files')
    parser.add_argument('--output-dir', default='split_videos', help='Output directory')
    args = parser.parse_args()

    try:
        check_ffmpeg()
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        temp_dir = Path('temp_extracted')  # Temporary directory for extracted files

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        output_dir.mkdir(exist_ok=True)
        temp_dir.mkdir(exist_ok=True)

        # Extract ZIP files
        extract_zip_files(input_dir, temp_dir)

        # Get all media files (videos and images)
        media_files = get_media_files(input_dir) + get_media_files(temp_dir)

        if not media_files:
            logging.warning("No media files found in input directory")
            return

        for media_file in media_files:
            if media_file.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']:
                try:
                    parts = split_video(media_file, output_dir)
                    logging.info(f"Created {len(parts)} parts for {media_file.name}")
                except Exception as e:
                    logging.error(f"Failed to process {media_file.name}: {str(e)}")
            else:
                # Copy images to the output directory
                try:
                    output_path = output_dir / media_file.name
                    output_path.write_bytes(media_file.read_bytes())
                    logging.info(f"Copied image {media_file.name} to {output_dir}")
                except Exception as e:
                    logging.error(f"Failed to copy image {media_file.name}: {str(e)}")

        # Run the bot to send videos and images
        run_bot()

        # Clean up temporary directory
        for file in temp_dir.rglob('*'):
            file.unlink()
        temp_dir.rmdir()

    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
