import os
import discord
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
UPLOAD_FOLDER = 'split_video'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def group_files_by_base(files):
    """Group files by their base name (without _part_xxx for videos)."""
    file_groups = defaultdict(list)
    for file in files:
        if '_part_' in file.stem:
            base_name = file.stem.rsplit('_part_', 1)[0]
            file_groups[base_name].append(file)
        else:
            file_groups[file.stem].append(file)

    # Sort each group by part number (if applicable)
    for base_name in file_groups:
        file_groups[base_name].sort(key=lambda x: x.name)

    return file_groups

async def send_file_group(channel, files):
    """Send a group of up to 10 files in a single Discord message."""
    try:
        await channel.send(files=[discord.File(str(file)) for file in files])
        print(f"Sent {len(files)} files to Discord in one message")
        # Remove files after sending
        for file in files:
            file.unlink()
    except Exception as e:
        print(f"Failed to send files: {e}")

async def send_files():
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("Error: Channel not found")
        return

    upload_path = Path(UPLOAD_FOLDER)
    if not upload_path.exists():
        print("No files to send")
        return

    # Get all files and group them
    all_files = list(upload_path.glob('*'))
    file_groups = group_files_by_base(all_files)

    # Send files in groups
    for base_name, files in file_groups.items():
        # Split into chunks of up to 10 files
        for i in range(0, len(files), 10):
            await send_file_group(channel, files[i:i+10])

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    try:
        await send_files()
    finally:
        await client.close()

def main():
    try:
        asyncio.run(client.start(DISCORD_TOKEN))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()