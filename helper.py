import logging
import subprocess
import asyncio
import os
import time, shutil
import subprocess
from Cryptodome.Cipher import AES
import base64
from Cryptodome.Util.Padding import unpad
from subprocess import getstatusoutput
import aiohttp
import aiofiles

# Global variables for optimization
failed_counter = 0

def decrypt_encrypted_mpd_key(url):
    key = b'638udh3829162018'
    iv = b'fedcba9876543210'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = base64.b64decode(url.encode('utf-8'))
    decrypted_data = cipher.decrypt(ciphertext)
    decrypted_data = unpad(decrypted_data, AES.block_size)
    mpd, keys = decrypted_data.decode().split(" * ")
    return mpd, keys

def duration(filename):
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30)
        return float(result.stdout)
    except Exception as e:
        logging.error(f"Duration error: {e}")
        return 0

async def download_video(url, cmd, name):
    """Optimized download function with better error handling"""
    # MAXIMUM SPEED download command
    download_cmd = f'{cmd} --no-part --retries 10 --fragment-retries 25 --concurrent-fragments 10 --external-downloader aria2c --downloader-args "aria2c: -x 16 -s 16 -k 5M -j 16 --min-split-size=5M --max-concurrent-downloads=16 --file-allocation=none --allow-overwrite=true"'
    
    global failed_counter
    print(f"🚀 Fast Download: {download_cmd}")
    logging.info(download_cmd)
    
    try:
        # Run with timeout
        k = subprocess.run(download_cmd, shell=True, timeout=3600)
        
        if "visionias" in cmd and k.returncode != 0 and failed_counter <= 5:
            failed_counter += 1
            await asyncio.sleep(3)
            return await download_video(url, cmd, name)
            
        failed_counter = 0
        
        # Fast file detection
        possible_extensions = ['', '.mp4', '.mkv', '.webm', '.mp4.webm']
        for ext in possible_extensions:
            full_name = name if ext == '' else f"{name.split('.')[0]}{ext}"
            if os.path.isfile(full_name):
                return full_name
                
        return f"{name.split('.')[0]}.mp4"
        
    except subprocess.TimeoutExpired:
        logging.error("Download timeout")
        return await download_video(url, cmd, name)
    except Exception as e:
        logging.error(f"Download error: {e}")
        return f"{name.split('.')[0]}.mp4"

async def download_kalam_video(url, name):
    """Optimized Kalam download with faster settings"""
    try:
        headers = [
            'User-Agent: okhttp/4.12.0',
            'Connection: keep-alive', 
            'Accept: */*',
            'Accept-Encoding: gzip, deflate, br',
            'mobilenumber: aDhYejdQcVIyd0IxazlEZg==',
            'referer: https://testing-news.kalampublication.in'
        ]
        
        header_args = " ".join([f'--add-header "{header}"' for header in headers])
        
        # MAXIMUM SPEED download command
        cmd = f'yt-dlp {header_args} --no-part --retries 5 --fragment-retries 10 --concurrent-fragments 10 --external-downloader aria2c --downloader-args "aria2c: -x 16 -s 16 -k 5M -j 16 --min-split-size=5M --max-concurrent-downloads=16 --file-allocation=none --allow-overwrite=true" -o "{name}.mp4" "{url}"'
        
        print(f"🚀 Turbo Kalam Download: {cmd}")
        logging.info(cmd)
        
        k = subprocess.run(cmd, shell=True, timeout=1800)
        
        if k.returncode != 0:
            await asyncio.sleep(2)
            return await download_kalam_video(url, name)
            
        # Quick file check
        for ext in ['.mp4', '.mkv', '.webm']:
            if os.path.isfile(f"{name}{ext}"):
                return f"{name}{ext}"
                
        return f"{name}.mp4"
        
    except Exception as e:
        logging.error(f"Kalam download error: {e}")
        raise e

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def time_formatter(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

last_update_time = {}

async def progress_bar(current, total, reply, start_time):
    """Stylish and Premium Upload Progress Bar with Anti-FloodWait"""
    try:
        now = time.time()
        diff = now - start_time
        
        # Skip if less than 1 second since start
        if diff < 1:
            return
        
        # Anti-FloodWait: Update only every 4 seconds
        message_id = reply.id
        if message_id in last_update_time:
            if now - last_update_time[message_id] < 4:
                return
        
        last_update_time[message_id] = now
        
        percentage = current * 100 / total
        speed = current / diff
        eta = (total - current) / speed if speed > 0 else 0
        
        # Create stylish progress bar
        filled_length = int(20 * current // total)
        bar = '█' * filled_length + '░' * (20 - filled_length)
        
        # Premium formatted message
        progress_text = (
            f"╭─────────────────────╮\n"
            f"│   📤 **UPLOADING**   │\n"
            f"╰─────────────────────╯\n\n"
            f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃ {bar} ┃\n"
            f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"📊 **Progress:** `{percentage:.1f}%`\n"
            f"📦 **Size:** `{humanbytes(current)}` / `{humanbytes(total)}`\n"
            f"⚡ **Speed:** `{humanbytes(speed)}/s`\n"
            f"⏱️ **ETA:** `{time_formatter(eta)}`\n\n"
            f"🔰 **Premium Upload in Progress** 🔰"
        )
        
        await reply.edit_text(progress_text)
        
    except Exception as e:
        pass

async def send_vid(bot, m, cc, filename, thumb, name, prog, url, channel_id):
    """ULTRA FAST UPLOAD FUNCTION"""
    
    # Delete progress message immediately
    await prog.delete(True)
    
    # Send upload message
    reply = await bot.send_message(
        channel_id, 
        f"**🚀 Starting Upload 🚀**\n\n**Name:** `{name}`\n\nPreparing..."
    )
    
    # PARALLEL PROCESSING: Generate thumbnail while getting duration
    final_thumb = None
    video_duration = 0
    
    async def generate_thumbnail():
        nonlocal final_thumb
        try:
            if thumb.startswith(("http://", "https://")):
                # Fast download with wget
                subprocess.run(f'wget -q --timeout=10 "{thumb}" -O "temp_thumb.jpg"', shell=True)
                if os.path.exists("temp_thumb.jpg"):
                    final_thumb = "temp_thumb.jpg"
                    
            elif thumb.lower() == "no" or True:  # Always generate auto thumbnail
                # Fast thumbnail generation
                thumb_cmd = f'ffmpeg -i "{filename}" -ss 00:00:05 -vframes 1 -y "auto_thumb.jpg"'
                subprocess.run(thumb_cmd, shell=True, timeout=10)
                if os.path.exists("auto_thumb.jpg"):
                    final_thumb = "auto_thumb.jpg"
                    
        except Exception as e:
            logging.error(f"Thumbnail error: {e}")
    
    async def get_duration():
        nonlocal video_duration
        try:
            video_duration = int(duration(filename))
        except:
            video_duration = 0
    
    # Run both tasks in parallel
    await asyncio.gather(
        generate_thumbnail(),
        get_duration(),
        return_exceptions=True
    )
    
    # UPLOAD WITH OPTIMIZED SETTINGS
    start_time = time.time()
    
    try:
        upload_args = {
            'chat_id': channel_id,
            'video': filename,
            'caption': cc,
            'supports_streaming': True,
            'duration': video_duration,
            'progress': progress_bar,
            'progress_args': (reply, start_time)
        }
        
        # Add thumbnail if available
        if final_thumb and os.path.exists(final_thumb):
            upload_args['thumb'] = final_thumb
        
        # HIGH SPEED UPLOAD
        await bot.send_video(**upload_args)
        
    except Exception as e:
        logging.error(f"Upload error: {e}")
        # Fallback without thumbnail
        try:
            await bot.send_video(
                chat_id=channel_id,
                video=filename,
                caption=cc,
                progress=progress_bar,
                progress_args=(reply, start_time)
            )
        except Exception as e2:
            logging.error(f"Fallback upload also failed: {e2}")
    
    # FAST CLEANUP
    try:
        # Remove main video file
        if os.path.exists(filename):
            os.remove(filename)
        
        # Remove thumbnail files
        for temp_file in ["temp_thumb.jpg", "auto_thumb.jpg", "Local_thumb.jpg"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
    except Exception as e:
        logging.error(f"Cleanup error: {e}")
    
    # Delete upload message
    await reply.delete(True)

async def download_and_dec_video(mpd, keys, path, name, raw_text2):
    """Optimized download and decrypt"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    
    # MAXIMUM SPEED download command
    download_cmd = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo[height<={int(raw_text2)}]+bestaudio" --no-part --concurrent-fragments 10 --external-downloader aria2c --downloader-args "aria2c: -x 16 -s 16 -k 5M -j 16 --min-split-size=5M --max-concurrent-downloads=16 --file-allocation=none" --allow-unplayable-format "{mpd}"'
    
    print(f"🚀 Fast MPD Download: {download_cmd}")
    subprocess.run(download_cmd, shell=True, timeout=1800)
    
    # Parallel decryption
    avDir = os.listdir(path)
    print("🔓 Parallel Decrypting...")
    
    decryption_commands = []
    for data in avDir:
        if data.endswith("mp4"):
            decryption_commands.append(f'mp4decrypt {keys} "{path}/{data}" "{path}/video.mp4"')
        elif data.endswith("m4a"):
            decryption_commands.append(f'mp4decrypt {keys} "{path}/{data}" "{path}/audio.m4a"')
    
    # Run decryption in parallel
    processes = []
    for cmd in decryption_commands:
        processes.append(subprocess.Popen(cmd, shell=True))
    
    # Wait for all to complete
    for p in processes:
        p.wait()
    
    # Cleanup original files
    for data in avDir:
        if os.path.exists(f'{path}/{data}'):
            os.remove(f'{path}/{data}')

async def merge_and_send_vid(bot, m, cc, name, prog, path, url, thumb, channel_id):
    """Optimized merge and upload"""
    
    # Fast merging
    video_path = os.path.join(path, "video.mp4")  
    audio_path = os.path.join(path, "audio.m4a") 
    final_video = f"{os.path.join(path, name)}.mp4"
    
    # Quick merge
    merge_cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c copy -y "{final_video}"'
    subprocess.run(merge_cmd, shell=True, timeout=300)
    
    # Clean intermediate files immediately
    for temp_file in [video_path, audio_path]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # Delete progress message
    await prog.delete(True)
    
    # Use the optimized send function
    await send_vid(bot, m, cc, final_video, thumb, name, 
                  await bot.send_message(channel_id, "Merging Complete"), 
                  url, channel_id)

# Additional optimization function
async def optimize_video_for_upload(filename):
    """Optional: Optimize video for faster upload"""
    try:
        optimized_file = f"optimized_{filename}"
        # Fast optimization without re-encoding if possible
        cmd = f'ffmpeg -i "{filename}" -c copy -movflags +faststart -y "{optimized_file}"'
        subprocess.run(cmd, shell=True, timeout=300)
        
        if os.path.exists(optimized_file):
            os.remove(filename)
            return optimized_file
        return filename
    except:
        return filename
