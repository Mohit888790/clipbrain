"""RQ queue configuration and utilities."""

from redis import Redis
from rq import Queue
from config import settings


# Parse Redis URL
redis_conn = Redis.from_url(settings.redis_url, decode_responses=False)

# Create default queue with 30-minute timeout
default_queue = Queue("default", connection=redis_conn, default_timeout=1800)


def enqueue_job(func, *args, **kwargs):
    """
    Enqueue a job to the default queue.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Job instance
    """
    return default_queue.enqueue(func, *args, **kwargs)


def get_job_status(job_id: str) -> dict:
    """
    Get job status.
    
    Args:
        job_id: Job ID
    
    Returns:
        Dictionary with job status information
    """
    from rq.job import Job
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        return {
            "id": job.id,
            "status": job.get_status(),
            "result": job.result,
            "exc_info": job.exc_info,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
    except Exception as e:
        return {
            "id": job_id,
            "status": "not_found",
            "error": str(e)
        }
