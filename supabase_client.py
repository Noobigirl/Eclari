import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not key:
    raise ValueError("SUPABASE_KEY environment variable is not set")

supabase = create_client(url, key)