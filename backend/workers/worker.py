"""RQ worker process."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from redis import Redis
from rq import Worker
from config import settings


def main():
    """Start RQ worker."""
    redis_conn = Redis.from_url(settings.redis_url, decode_responses=False)
    
    worker = Worker(
        ["default"],
        connection=redis_conn,
        name="clipbrain-worker"
    )
    
    print("🚀 Starting ClipBrain worker...")
    print(f"   Listening on queue: default")
    print(f"   Redis: {settings.redis_url[:50]}...")
    
    worker.work()


if __name__ == "__main__":
    main()
