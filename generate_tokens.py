import jwt
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.environ.get("MCP_JWT_SECRET")

users = ["Yutong", "Bruno", "test"]

for username in users:
    token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=90)
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    print(f"{username}: {token}")