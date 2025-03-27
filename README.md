# Video Splitter and Discord Uploader

This project provides a tool to split large video files into smaller segments (~10MB each) and upload them to a Discord channel using a bot.

## Features
- Splits video files into smaller segments using FFmpeg.
- Automatically calculates the number of segments based on video size and bitrate.
- Uploads the split video segments to a specified Discord channel.
- Supports multiple video formats (e.g., `.mp4`, `.mkv`, `.avi`, etc.).

## Requirements
- Python 3.8 or higher
- FFmpeg installed and placed in the `ffmpeg` directory.
- A Discord bot token and channel ID.

## Installation
1. Clone the repository:
```bash 
    git clone https://github.com/Exill18/Splitter.git
    cd Splitter
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Download and extract FFmpeg binaries:

Download FFmpeg from [FFmpeg Builds](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z).
Extract the contents into a folder named **ffmpeg** in the project directory.

4. Create a **.env** file in the project root with the following content:
DISCORD_TOKEN=your_discord_bot_token
CHANNEL_ID=your_discord_channel_id


## Usage

Splitting Videos
Run the video_splitter.py script to split videos:

python [video_splitter.py](http://_vscodecontentref_/0) <input_directory> --output-dir <output_directory>

**<input_directory>**: Path to the folder containing video files.
**--output-dir: (Optional)** Path to the folder where split videos will be saved. Defaults to split_videos.

## Uploading Videos to Discord channel
The video_splitter.py script automatically runs the Discord bot (bot.py) after splitting videos. The bot uploads the split videos to the specified Discord channel. So make sure that the Bot token and Channel ID are set in the .env

## File Structure

.
├── [bot.py](https://github.com/Exill18/projInt/blob/main/bot.py)                # Discord bot script for uploading videos
├── [video_splitter.py](https://github.com/Exill18/projInt/blob/main/video_splitter.py)     # Main script for splitting videos
├── ffmpeg/               # Directory containing FFmpeg binaries
├── .env                  # Environment variables (Discord token and channel ID)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation


License
This project is licensed under the MIT License. See the LICENSE file for details.
