from datetime import datetime

class idutils:
    @staticmethod
    def generate_id():
        return int((datetime.utcnow() - datetime(2015, 1, 1)).total_seconds() * 1000) << 22

    def datetimefromid(snowflake: int):
        return datetime.utcfromtimestamp(((snowflake >> 22) + 1420070400000)/1000)
