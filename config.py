import os

# Environment variables set karna
os.environ["BOT_TOKEN"] = "6047785902:AAE59KTfmhRvF8sUSYIzl9wcGnm4FLXiWDk"
os.environ["API_ID"] = "24250238"
os.environ["API_HASH"] = "cb3f118ce5553dc140127647edcf3720"
os.environ["VIP_USER"] = "6175650047"

class Config(object):
    # Bot configuration variables
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    
    # VIP users ko handle karna
    VIP_USER = os.environ.get("VIP_USER", '')
    VIP_USERS = [int(user_id.strip()) for user_id in VIP_USER.split(',') if user_id.strip()]
