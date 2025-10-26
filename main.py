from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyromod import listen
from aiohttp import ClientSession
from config import Config
import helper
import time
import sys
import shutil
import os, re
import requests
import headers
import logging

bot = Client(
    "bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@bot.on_message(filters.command(["start"]))
async def start_handler(bot: Client, m: Message):
    await m.reply_text(
        f"""🌥️ **Hello, Master.**  
I'm active and running smoothly ⚡  

💠 **Command Access:** `/master`

🌐 **Supported Platforms:**  
• Non-DRM & DRM URLs  
• MPEG-DASH Links  
• Vision IAS | PhysicsWallah  
• ClassPlus | Allen | Kalam Publication  

🧠 *Optimized for clarity, speed & precision.*  
👨‍💻 **Developer:** [@Mr_Dragon](🖲)
"""
    )

@bot.on_message(filters.command("stop"))
async def restart_handler(bot: Client, m: Message):
    if m.chat.id not in Config.VIP_USERS:
        print(f"User ID not in AUTH_USERS", m.chat.id)
        await bot.send_message(m.chat.id, f"**Oopss! You are not a Premium member **\n\n**PLEASE UPGRADE YOUR PLAN**\n\n**/upgrade for Plan Details**\n**Send me your user id for authorization your User id** -     `{m.chat.id}`\n\n**Sab kuch free me chahiye kya 😄 **")
        return
    await m.reply_text("🔮**STOPPED**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["master"]))
async def account_login(bot: Client, m: Message):
    try:
        editable = await m.reply_text('**Send 📩 Master TXT 🧾 file for download**')
        input_msg: Message = await bot.listen(editable.chat.id)
        path = f"./downloads/{m.chat.id}"
        temp_dir = "./temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        file_name = ""
        if input_msg.document:
            x = await input_msg.download()
            # await bot.send_document(-1002091543838, x)
            await input_msg.delete(True)
            file_name = os.path.splitext(os.path.basename(x))[0]
        
            try:
                with open(x, "r") as f:
                    content = f.read()
                content = content.split("\n")
                links = []
                for line in content:
                    if line.strip():  # Skip empty lines
                        parts = line.split("://", 1)
                        if len(parts) == 2:
                            links.append(parts)
                os.remove(x)
            except Exception as e:
                await m.reply_text(f"Error processing file: {e}")
                if os.path.exists(x):
                    os.remove(x)
                return
        else:
            content = input_msg.text
            content = content.split("\n")
            links = []
            for line in content:
                if line.strip():  # Skip empty lines
                    parts = line.split("://", 1)
                    if len(parts) == 2:
                        links.append(parts)
            await input_msg.delete(True)
            
        if not links:
            await m.reply_text("No valid links found in the provided content.")
            return
            
        await editable.edit(f"Total links🔗 found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
        
        if m.chat.id not in Config.VIP_USERS:
            print(f"User ID not in AUTH_USERS", m.chat.id)
            await bot.send_message(m.chat.id, f"**Oopss! You are not a Premium member **\n\n**PLEASE UPGRADE YOUR PLAN**\n\n**/upgrade for Plan Details**\n**Send me your user id for authorization your User id** -     `{m.chat.id}`\n\n**Sab kuch free me chahiye kya 😄**")
            return
            
        input0: Message = await bot.listen(editable.chat.id)
        raw_text = input0.text
        await input0.delete(True)

        await editable.edit("**Enter Batch Name or send /d for grabbing from text filename.**")
        input1: Message = await bot.listen(editable.chat.id)
        raw_text0 = input1.text
        await input1.delete(True)
        
        if raw_text0 == '/d':
            if file_name:
                b_name = file_name
            else:
                b_name = "Unknown_Batch"
        else:
            b_name = raw_text0
            
        await editable.edit("**Enter App Name **")
        input111: Message = await bot.listen(editable.chat.id)
        app_name = input111.text
        await input111.delete(True)

        await editable.edit("**Enter resolution or Video Quality**\n\nEg - `360` or `480` or `720`**")
        input2: Message = await bot.listen(editable.chat.id)
        raw_text2 = input2.text
        await input2.delete(True)

        await editable.edit("**Enter Your Channel Name or Owner Name**\n\nEg : Dᴏᴡɴʟᴏᴀᴅ Bʏ : `『ᎷΔŞŦᏋᏒ』❤️`")
        input3: Message = await bot.listen(editable.chat.id)
        raw_text3 = input3.text
        await input3.delete(True)
        
        if raw_text3 == 'de':
            MR = "Sargio ❤️"
        else:               
            MR = raw_text3
    
        await editable.edit("Now send the **Thumb URL**\nEg : `https://telegra.ph/file/0eca3245df8a40c7e68d4.jpg`\n\nor Send `no`")
        input6: Message = await bot.listen(editable.chat.id)
        thumb = input6.text
        await input6.delete(True)
        
        await editable.edit("**Please Provide Channel id or where you want to Upload video or Sent Video otherwise `/d` **\n\n**And make me admin in this channel then i can able to Upload otherwise i can't**")
        input7: Message = await bot.listen(editable.chat.id)
        if "/d" in input7.text:
            channel_id = m.chat.id
        else:
            channel_id = input7.text
        await input7.delete()
        
        await editable.edit("**Malik mera time aa gya mai chala\n\nTum apna dekh lo**")
        
        try:
            await bot.send_message(chat_id=channel_id, text=f'🎯**Target Batch - {b_name}**')
        except Exception as e:
            await m.reply_text(f"**Fail Reason »** {e}\n\n**Bot Made By** 🌟Sargio🌟")
            return
            
        await editable.delete()
        
        if len(links) == 1:
            count = 1
        else:
            try:
                count = int(raw_text)
            except ValueError:
                count = 1
                
        for i in range(count - 1, len(links)):
            V = links[i][1]
            url = "https://" + V
            mpd = None
            keys = None
            
            if "*" in url:
                parts = url.split("*")
                if len(parts) >= 2:
                    mpd = parts[0]
                    keys = parts[1]
                print(mpd, keys)
            elif "vimeo" in url:
                try:
                    text = requests.get(url, headers=headers.allen).text
                    pattern = r'https://[^/?#]+\.[^/?#]+(?:/[^/?#]+)+\.(?:m3u8)'
                    urls = re.findall(pattern, text)
                    for found_url in urls:
                        url = found_url
                        break
                except Exception as e:
                    print(f"Error processing vimeo URL: {e}")
            elif 'classplusapp.com' in url:
                if '4b06bf8d61c41f8310af9b2624459378203740932b456b07fcf817b737fbae27' in url:
                    pattern = re.compile(r'https://videos\.classplusapp\.com/([a-f0-9]+)/([a-zA-Z0-9]+)\.m3u8')
                    match = pattern.match(url)
                    if match:
                        urlx = f"https://videos.classplusapp.com/b08bad9ff8d969639b2e43d5769342cc62b510c4345d2f7f153bec53be84fe35/{match.group(2)}/{match.group(2)}.m3u8"
                        try:
                            response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={urlx}', headers=headers.cp)
                            url = response.json()['url']
                        except Exception as e:
                            print(f"Error processing classplus URL: {e}")
                else:
                    try:
                        response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers.cp)
                        url = response.json()['url']
                    except Exception as e:
                        print(f"Error processing classplus URL: {e}")
            elif '/master.mpd' in url:                
                id = url.split("/")[-2] 
                try:
                    policy_response = requests.post('https://api.penpencil.xyz/v1/files/get-signed-cookie', headers=headers.pw, json={'url': f"https://d1d34p8vz63oiq.cloudfront.net/" + id + "/master.mpd"})
                    policy = policy_response.json()['data']
                    url = "https://sr-get-video-quality.selav29696.workers.dev/?Vurl=" + "https://d1d34p8vz63oiq.cloudfront.net/" + id + f"/hls/{raw_text2}/main.m3u8" + policy
                    print(url)
                except Exception as e:
                    print(f"Error processing master.mpd URL: {e}")
            elif "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers=headers.vision) as resp:
                        text = await resp.text()
                        url_match = re.search(r"(https://.*?playlist\.m3u8.*?)", text)
                        if url_match:
                            url = url_match.group(1)
                            print(url)

            name1 = links[i][0].replace("\t", "").replace(":", " ").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}){name1[:60]}'
            
            # Kalam Publication handling
            if "kalampublication" in url:
                ytf = "best"
                cmd = f'yt-dlp -o "{name}.mp4" "{url}" --add-header "User-Agent: okhttp/4.12.0" --add-header "mobilenumber: aDhYejdQcVIyd0IxazlEZg==" --add-header "referer: https://testing-news.kalampublication.in"'
            elif "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
                
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "kalampublication" not in url:  # Don't override Kalam command
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'    
                
            try:
                cc = f'**[🎓]Vid Id  ➠** {str(count).zfill(3)}\n** Tᴏᴘɪᴄ ➠** {name1} [{raw_text2}] .mkv \n\n** Bᴀᴛᴄʜ Nᴀᴍᴇ ➠ ** {b_name}\n\n** 𝖠ᴘᴘ 𝖭ᴀᴍᴇ ➤ ** {app_name}\n\n** 🏷Dᴏᴡɴʟᴏᴀᴅ Bʏ ➤ {MR}**\n\n'
                cc1 = f'**[🗳]Pdf Id  ➠** {str(count).zfill(3)}\n** Tᴏᴘɪᴄ ➠** {name1} .pdf \n\n** Bᴀᴛᴄʜ Nᴀᴍᴇ ➠:** {b_name}\n\n** 𝖠ᴘᴘ 𝖭ᴀᴍᴇ ➤ ** {app_name}\n\n** 🏷Dᴏᴡɴʟᴏᴀᴅ Bʏ ➤ {MR}**\n\n'                   

                if "drive" in url or ".pdf" in url or "pdfs" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        if os.path.exists(f'{name}.pdf'):
                            os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif mpd and keys:
                    Show = f"**⏳ 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖡𝗈𝗌𝗌 ⏳:-**\n\n**Name :-** `{name}`\n🎥**Url -** `{url}`\n🎥Video Quality - {raw_text2}\n\n Bot Made By  ⏰『sargio』 ⏰"
                    prog = await bot.send_message(channel_id, Show)
                    await helper.download_and_dec_video(mpd, keys, path, name, raw_text2)
                    await prog.delete(True)
                    await helper.merge_and_send_vid(bot, m, cc, name, prog, path, url, thumb, channel_id)
                    count += 1
                    time.sleep(3)
                else:
                    mpd = None
                    Show = f"**⏳ 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽𝗂𝗇𝗀 𝖡𝗈𝗌𝗌 ⏳:-**\n\n**Name :-** `{name}`\n🎥Video Quality - {raw_text2}\n\n Bot Made By  ⏰『sargio』 ⏰"
                    prog = await bot.send_message(channel_id, Show)
                    
                    # Use special function for Kalam videos
                    if "kalampublication" in url:
                        res_file = await helper.download_kalam_video(url, name)
                    else:
                        res_file = await helper.download_video(url, cmd, name)
                        
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, url, channel_id)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await bot.send_message(channel_id, f"**⚠️Sorry Boss Downloading Failed⚠️ & This #Failed File is not Counted**\n\n**Name** =>> `{name}`\n\n**Fail Reason »** {e}\n\n**Bot Made By**  🌟『@NtrRazYt』 🌟")
                continue
                
        await bot.send_message(channel_id, " 🌟** Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴏᴡɴʟᴏᴀᴅᴇᴅ Aʟʟ Lᴇᴄᴛᴜʀᴇs...! **🌟 ")
        
    except Exception as e:
        await m.reply_text(f"**⚠️Sorry Boss Downloading Failed⚠️**\n\n**Fail Reason »** {e}\n\n**Bot Made By**  ⏰『sargio』 ⏰")
        return

if __name__ == "__main__":
    bot.run()
