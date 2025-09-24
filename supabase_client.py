from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv() # pre loading the .env file

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY") # fetching the environment variables

supabase = create_client(url, key)