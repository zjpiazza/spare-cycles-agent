import asyncio
from gpustat import GPUStatCollection
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
update_interval = int(os.getenv("UPDATE_INTERVAL", 5))

supabase = create_client(supabase_url, supabase_key)

async def get_gpu_stats():
    """Get GPU statistics in a dictionary format"""
    stats = GPUStatCollection.new_query()
    gpu = stats[0]
    properties = gpu.entry
    
    return {
        "timestamp": datetime.now().isoformat(),
        "gpu_name": properties['name'],
        "temperature": properties['temperature.gpu'],
        "fan_speed": properties['fan.speed'],
        "memory_total": properties['memory.total'],
        "memory_used": properties['memory.used'],
        "utilization": properties['utilization.gpu'],
        "power_draw": properties['power.draw'],
        "power_limit": properties['enforced.power.limit']
    }

async def store_stats():
    """Store GPU stats in Supabase database every second"""
    while True:
        try:
            stats = await get_gpu_stats()
            # Insert stats into Supabase
            supabase.table('gpu_stats').insert(stats).execute()
            print(f"Stored stats at {stats['timestamp']}")
        except Exception as e:
            print(f"Error storing stats: {e}")
        
        await asyncio.sleep(update_interval)

if __name__ == "__main__":
    asyncio.run(store_stats())
