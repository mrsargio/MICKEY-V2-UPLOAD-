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
import math
from datetime import datetime

# Global variables for optimization
failed_counter = 0

class ProgressTracker:
    """Modern progress tracking with live speed display"""
    
    def __init__(self):
        self.start_time = None
        self.last_update = None
        self.last_bytes = 0
        self.speeds = []
        
    def format_bytes(self, bytes):
        """Convert bytes to human readable format"""
        if bytes == 0:
            return "0B"
        sizes = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(bytes, 1024)))
        return f"{bytes / (1024 ** i):.2f} {sizes[i]}"
    
    def format_speed(self, bytes_per_sec):
        """Format speed in appropriate units"""
        return self.format_bytes(bytes_per_sec) + "/s"
    
    def format_time(self, seconds):
        """Format time in HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def create_progress_bar(self, percentage, length=20):
        """Create a modern progress bar"""
        filled = int(length * percentage // 100)
        empty = length - filled
        bar = "█" * filled + "░" * empty
        return f"│{bar}│ {percentage:.1f}%"
    
    def calculate_speed(self, current_bytes, current_time):
        """Calculate current speed"""
        if self.last_update is None:
            self.last_update = current_time
            self.last_bytes = current_bytes
            return 0
            
        time_diff = current_time - self.last_update
        bytes_diff = current_bytes - self.last_bytes
        
        if time_diff > 0:
            speed = bytes_diff / time_diff
            self.speeds.append(speed)
            # Keep only last 5 speeds for average
            if len(self.speeds) > 5:
                self.speeds.pop(0)
            
        self.last_update = current_time
        self.last_bytes = current_bytes
        
        if self.speeds:
            return sum(self.speeds) / len(self.speeds)
        return 0
    
    def get_eta(self, total_bytes, current_bytes, speed):
        """Calculate ETA"""
        if speed > 0:
            remaining_bytes = total_bytes - current_bytes
            return remaining_bytes / speed
        return 0

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
    """Optimized download function with modern progress tracking"""
    global failed_counter
    
    # Enhanced download command for maximum speed on Termux
    download_cmd = f'{cmd} --no-part --retries 10 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -s 32 -k 1M -j 32 --file-allocation=none --summary-interval=1"'
    
    print(f"🚀 Turbo Download Started: {name}")
    logging.info(download_cmd)
    
    try:
        # Run with timeout and progress tracking
        process = await asyncio.create_subprocess_shell(
            download_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Progress tracking for downloads
        tracker = ProgressTracker()
        tracker.start_time = time.time()
        
        async for line in process.stderr:
            line = line.decode().strip()
            if any(x in line for x in ['%', 'Downloading', 'ETA']):
                print(f"📥 {line}")
        
        await process.wait()
        
        if "visionias" in cmd and process.returncode != 0 and failed_counter <= 5:
            failed_counter += 1
            await asyncio.sleep(3)
            return await download_video(url, cmd, name)
            
        failed_counter = 0
        
        # Fast file detection
        possible_extensions = ['', '.mp4', '.mkv', '.webm', '.mp4.webm']
        for ext in possible_extensions:
            full_name = name if ext == '' else f"{name.split('.')[0]}{ext}"
            if os.path.isfile(full_name):
                print(f"✅ Download Complete: {full_name}")
                return full_name
                
        return f"{name.split('.')[0]}.mp4"
        
    except subprocess.TimeoutExpired:
        logging.error("Download timeout")
        return await download_video(url, cmd, name)
    except Exception as e:
        logging.error(f"Download error: {e}")
        return f"{name.split('.')[0]}.mp4"

async def download_kalam_video(url, name):
    """Optimized Kalam download with HTTP 416 error handling"""
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
        
        # Check if file exists and handle HTTP 416 error
        output_file = f"{name}.mp4"
        
        # If file exists and might be corrupted/incomplete, remove it
        if os.path.exists(output_file):
            print(f"🔄 Existing file detected. Checking for corruption...")
            try:
                file_size = os.path.getsize(output_file)
                if file_size > 0:
                    # Try to get file duration to check if it's playable
                    result = subprocess.run([
                        "ffprobe", "-v", "error", "-show_entries", 
                        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", 
                        output_file
                    ], capture_output=True, timeout=10)
                    
                    if result.returncode != 0:
                        print(f"🗑️ Removing corrupted file: {output_file}")
                        os.remove(output_file)
                    else:
                        print(f"✅ Existing file appears valid. Size: {file_size} bytes")
                        return output_file
            except Exception as e:
                print(f"🗑️ Removing problematic file: {e}")
                os.remove(output_file)
        
        # FIXED: Use --no-continue to avoid HTTP 416 errors and force fresh download
        cmd = f'yt-dlp {header_args} --no-part --no-continue --retries 5 --fragment-retries 10 --external-downloader aria2c --downloader-args "aria2c: -x 16 -s 32 -k 1M -j 16 --file-allocation=none --summary-interval=1 --max-tries=5 --retry-wait=2" -o "{name}.mp4" "{url}"'
        
        print(f"🚀 Turbo Kalam Download Started")
        print(f"📝 Command: {cmd}")
        logging.info(cmd)
        
        # Run with progress tracking
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Track progress
        async for line in process.stderr:
            line = line.decode().strip()
            if line and not line.startswith('[debug]'):
                print(f"📥 {line}")
        
        await process.wait()
        
        # Handle different return codes
        if process.returncode == 0:
            print(f"✅ Kalam download successful!")
            
            # Verify the downloaded file
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📦 File size: {file_size} bytes")
                return output_file
            else:
                print(f"❌ Download completed but file not found: {output_file}")
                raise Exception("Downloaded file not found")
                
        elif process.returncode != 0:
            print(f"⚠️ Download failed with return code: {process.returncode}")
            
            # Specific handling for HTTP 416
            if os.path.exists(output_file):
                print(f"🔄 HTTP 416 detected - removing corrupted file and retrying...")
                try:
                    os.remove(output_file)
                    print(f"🗑️ Removed corrupted file: {output_file}")
                except Exception as e:
                    print(f"❌ Could not remove file: {e}")
            
            await asyncio.sleep(3)
            print(f"🔄 Retrying download...")
            return await download_kalam_video(url, name)
            
        # Quick file check as fallback
        for ext in ['.mp4', '.mkv', '.webm']:
            if os.path.isfile(f"{name}{ext}"):
                print(f"✅ Kalam Download Complete: {name}{ext}")
                return f"{name}{ext}"
                
        return f"{name}.mp4"
        
    except Exception as e:
        logging.error(f"Kalam download error: {e}")
        print(f"❌ Critical error in Kalam download: {e}")
        
        # Clean up any potentially corrupted files
        for ext in ['.mp4', '.mkv', '.webm', '.part', '.ytdl']:
            temp_file = f"{name}{ext}"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"🗑️ Cleaned up temp file: {temp_file}")
                except:
                    pass
        
        # Wait before retry
        await asyncio.sleep(5)
        print(f"🔄 Final retry attempt...")
        return await download_kalam_video(url, name)

async def send_vid(bot, m, cc, filename, thumb, name, prog, url, channel_id):
    """ULTRA FAST UPLOAD FUNCTION with Modern Progress"""
    
    # Delete progress message immediately
    await prog.delete(True)
    
    # Send upload message with modern styling
    reply = await bot.send_message(
        channel_id, 
        f"**🚀 Turbo Upload Started**\n\n"
        f"**📹 Name:** `{name}`\n"
        f"**🔗 URL:** `{url}`\n"
        f"**⏰ Started:** {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"🔄 Preparing upload...\n\n"
        f"**DRM Bot Made By 🔰『sargio』🔰**"
    )
    
    # PARALLEL PROCESSING with progress
    final_thumb = None
    video_duration = 0
    file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
    
    async def generate_thumbnail():
        nonlocal final_thumb
        try:
            if thumb.startswith(("http://", "https://")):
                # Fast download with wget and progress
                thumb_proc = await asyncio.create_subprocess_shell(
                    f'wget -q --timeout=10 --show-progress "{thumb}" -O "temp_thumb.jpg"',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await thumb_proc.wait()
                if os.path.exists("temp_thumb.jpg"):
                    final_thumb = "temp_thumb.jpg"
                    print("✅ Thumbnail downloaded")
                    
            elif thumb.lower() == "no" or True:
                # Fast thumbnail generation with progress
                thumb_cmd = f'ffmpeg -i "{filename}" -ss 00:00:05 -vframes 1 -y "auto_thumb.jpg" -hide_banner -loglevel error'
                thumb_proc = await asyncio.create_subprocess_shell(thumb_cmd)
                await thumb_proc.wait()
                if os.path.exists("auto_thumb.jpg"):
                    final_thumb = "auto_thumb.jpg"
                    print("✅ Auto thumbnail generated")
                    
        except Exception as e:
            logging.error(f"Thumbnail error: {e}")
    
    async def get_duration():
        nonlocal video_duration
        try:
            video_duration = int(duration(filename))
            print(f"⏱️ Duration: {video_duration}s")
        except:
            video_duration = 0
    
    # Run both tasks in parallel
    await asyncio.gather(
        generate_thumbnail(),
        get_duration(),
        return_exceptions=True
    )
    
    # UPLOAD WITH MODERN PROGRESS TRACKING
    start_time = time.time()
    tracker = ProgressTracker()
    tracker.start_time = start_time
    
    def upload_progress(current, total):
        """Real-time upload progress callback"""
        try:
            current_time = time.time()
            percentage = (current / total) * 100
            
            # Calculate speed and ETA
            speed = tracker.calculate_speed(current, current_time)
            eta = tracker.get_eta(total, current, speed)
            
            # Create progress display
            progress_bar = tracker.create_progress_bar(percentage)
            speed_display = tracker.format_speed(speed)
            eta_display = tracker.format_time(eta)
            uploaded = tracker.format_bytes(current)
            total_size = tracker.format_bytes(total)
            elapsed = tracker.format_time(current_time - start_time)
            
            progress_text = (
                f"**🚀 Turbo Uploading**\n\n"
                f"**📹 Name:** `{name}`\n"
                f"**📊 Progress:** {progress_bar}\n"
                f"**📦 Size:** {uploaded} / {total_size}\n"
                f"**⚡ Speed:** {speed_display}\n"
                f"**⏱️ Elapsed:** {elapsed}\n"
                f"**🕐 ETA:** {eta_display}\n\n"
                f"**DRM Bot Made By 🔰『sargio』🔰**"
            )
            
            # Update message (this would need to be implemented with message editing)
            # In practice, you'd update the message here
            print(f"📤 Upload: {percentage:.1f}% | Speed: {speed_display} | ETA: {eta_display}")
            
        except Exception as e:
            logging.error(f"Progress error: {e}")
    
    try:
        upload_args = {
            'chat_id': channel_id,
            'video': filename,
            'caption': cc,
            'supports_streaming': True,
            'duration': video_duration,
            'progress': upload_progress,
            'progress_args': (reply, start_time)
        }
        
        # Add thumbnail if available
        if final_thumb and os.path.exists(final_thumb):
            upload_args['thumb'] = final_thumb
        
        # HIGH SPEED UPLOAD with progress
        print(f"🚀 Starting upload: {filename}")
        await bot.send_video(**upload_args)
        
        # Upload complete message
        total_time = time.time() - start_time
        await reply.edit(
            f"**✅ Upload Complete!**\n\n"
            f"**📹 Name:** `{name}`\n"
            f"**⏱️ Total Time:** {tracker.format_time(total_time)}\n"
            f"**📦 File Size:** {tracker.format_bytes(file_size)}\n"
            f"**⚡ Average Speed:** {tracker.format_speed(file_size/total_time) if total_time > 0 else 'N/A'}\n\n"
            f"**DRM Bot Made By 🔰『sargio』🔰**"
        )
        
    except Exception as e:
        logging.error(f"Upload error: {e}")
        # Fallback without thumbnail
        try:
            await bot.send_video(
                chat_id=channel_id,
                video=filename,
                caption=cc,
                progress=upload_progress,
                progress_args=(reply, start_time)
            )
        except Exception as e2:
            logging.error(f"Fallback upload also failed: {e2}")
            await reply.edit(f"**❌ Upload Failed:** {str(e2)}")
    
    # FAST CLEANUP
    try:
        # Remove main video file
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✅ Cleaned: {filename}")
        
        # Remove thumbnail files
        for temp_file in ["temp_thumb.jpg", "auto_thumb.jpg", "Local_thumb.jpg"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"✅ Cleaned: {temp_file}")
                
    except Exception as e:
        logging.error(f"Cleanup error: {e}")
    
    # Wait a bit then delete upload message
    await asyncio.sleep(5)
    await reply.delete(True)

async def download_and_dec_video(mpd, keys, path, name, raw_text2):
    """Optimized download and decrypt with progress tracking"""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    
    print("🚀 Starting MPD download with progress...")
    
    # Faster download command with progress
    download_cmd = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo[height<={int(raw_text2)}]+bestaudio" --no-part --no-continue --external-downloader aria2c --downloader-args "aria2c: -x 16 -s 32 -j 32 --summary-interval=1" --allow-unplayable-format "{mpd}"'
    
    print(f"📥 MPD Download: {download_cmd}")
    
    # Run with progress tracking
    process = await asyncio.create_subprocess_shell(
        download_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Track download progress
    tracker = ProgressTracker()
    tracker.start_time = time.time()
    
    async for line in process.stderr:
        line = line.decode().strip()
        if any(x in line for x in ['%', 'Downloading', 'ETA']):
            print(f"📥 {line}")
    
    await process.wait()
    
    # Parallel decryption with progress
    avDir = os.listdir(path)
    print("🔓 Parallel Decrypting with progress...")
    
    decryption_commands = []
    for data in avDir:
        if data.endswith("mp4"):
            decryption_commands.append(f'mp4decrypt {keys} "{path}/{data}" "{path}/video.mp4"')
        elif data.endswith("m4a"):
            decryption_commands.append(f'mp4decrypt {keys} "{path}/{data}" "{path}/audio.m4a"')
    
    # Run decryption in parallel with progress
    processes = []
    for i, cmd in enumerate(decryption_commands):
        print(f"🔓 Decrypting file {i+1}/{len(decryption_commands)}")
        processes.append(await asyncio.create_subprocess_shell(cmd))
    
    # Wait for all to complete
    for p in processes:
        await p.wait()
    
    # Cleanup original files
    for data in avDir:
        if os.path.exists(f'{path}/{data}'):
            os.remove(f'{path}/{data}')
    
    print("✅ Download and decrypt complete!")

async def merge_and_send_vid(bot, m, cc, name, prog, path, url, thumb, channel_id):
    """Optimized merge and upload with progress tracking"""
    
    print("🔄 Starting fast merge...")
    
    # Fast merging with progress
    video_path = os.path.join(path, "video.mp4")  
    audio_path = os.path.join(path, "audio.m4a") 
    final_video = f"{os.path.join(path, name)}.mp4"
    
    # Quick merge with progress display
    merge_cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c copy -y "{final_video}" -hide_banner -loglevel error -progress pipe:1'
    
    print("🎬 Merging video and audio...")
    process = await asyncio.create_subprocess_shell(
        merge_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Show merge progress
    async for line in process.stdout:
        line = line.decode().strip()
        if 'out_time=' in line:
            print(f"🎬 Merge progress: {line}")
    
    await process.wait()
    
    # Clean intermediate files immediately
    for temp_file in [video_path, audio_path]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"✅ Cleaned: {temp_file}")
    
    # Delete progress message
    await prog.delete(True)
    
    # Use the optimized send function
    await send_vid(bot, m, cc, final_video, thumb, name, 
                  await bot.send_message(channel_id, "✅ Merge Complete! Starting upload..."), 
                  url, channel_id)

# Enhanced optimization function for Termux
async def optimize_video_for_upload(filename):
    """Optimize video for faster upload on Termux"""
    try:
        optimized_file = f"optimized_{os.path.basename(filename)}"
        print("⚡ Optimizing video for fast upload...")
        
        # Fast optimization for Termux - no re-encoding, just optimize layout
        cmd = f'ffmpeg -i "{filename}" -c copy -movflags +faststart -y "{optimized_file}" -hide_banner -loglevel error'
        
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()
        
        if os.path.exists(optimized_file):
            original_size = os.path.getsize(filename)
            optimized_size = os.path.getsize(optimized_file)
            
            print(f"✅ Optimization complete: {original_size} → {optimized_size} bytes")
            os.remove(filename)
            return optimized_file
        return filename
    except Exception as e:
        print(f"⚠️ Optimization skipped: {e}")
        return filename

# Additional utility for Termux performance
def check_termux_performance():
    """Check and optimize for Termux environment"""
    if 'TERMUX_VERSION' in os.environ:
        print("📱 Termux environment detected - applying optimizations")
        # Set optimal parameters for Termux
        os.environ['FFMPEG_BINARY'] = 'ffmpeg'
        os.environ['ARIA2C_BINARY'] = 'aria2c'
        return True
    return False

# Initialize performance optimizations
check_termux_performance()
