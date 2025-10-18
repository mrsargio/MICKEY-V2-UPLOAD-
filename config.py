import os

class Config(object):
    BOT_TOKEN = os.environ.get("6047785902:AAE59KTfmhRvF8sUSYIzl9wcGnm4FLXiWDk")
    API_ID = int(os.environ.get("24250238"))
    API_HASH = os.environ.get("cb3f118ce5553dc140127647edcf3720")
    VIP_USER = os.environ.get('6175650047', '').split(',')
    VIP_USERS = [int(user_id) for user_id in VIP_USER]
