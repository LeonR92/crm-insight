import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
if not url or not key:
    raise ValueError("Missing Supabase credentials in .env file")
supabase: Client = create_client(url, key)
