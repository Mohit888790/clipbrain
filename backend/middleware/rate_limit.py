"""Rate limiting middleware using Redis."""

import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Define rate limits per endpoint
        rate_limits = {
            "/ingest": settings.ingest_rate_limit_per_hour,
            "/search": settings.search_rate_limit_per_hour,
        }
        
        # Check if endpoint needs rate limiting
        path = request.url.path
        limit = None
        for endpoint, endpoint_limit in rate_limits.items():
            if path.startswith(endpoint):
                limit = endpoint_limit
                break
        
        if limit:
            # Check rate limit
            key = f"ratelimit:{path}:{client_ip}"
            current_hour = int(time.time() / 3600)
            key_with_hour = f"{key}:{current_hour}"
            
            try:
                # Increment counter
                count = await self.redis_client.incr(key_with_hour)
                
                # Set expiry on first request
                if count == 1:
                    await self.redis_client.expire(key_with_hour, 3600)
                
                # Check if limit exceeded
                if count > limit:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Maximum {limit} requests per hour."
                    )
            except HTTPException:
                raise
            except Exception:
                # If Redis fails, allow request (fail open)
                pass
        
        response = await call_next(request)
        return response
