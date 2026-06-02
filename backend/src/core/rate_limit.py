"""Rate limiting using Redis."""

import time
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import get_settings
from src.db.session import get_redis

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""

    async def dispatch(self, request: Request, call_next: Callable):
        """Check rate limit before processing request."""
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        redis = await get_redis()
        if redis is None:
            # If Redis unavailable, allow request but log warning
            return await call_next(request)

        try:
            current_time = time.time()
            window_start = current_time - settings.rate_limit_window_seconds

            # Use Redis sorted set for sliding window
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.zcard(key)
            pipe.expire(key, settings.rate_limit_window_seconds)
            results = await pipe.execute()

            request_count = results[2]

            if request_count > settings.rate_limit_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                    headers={
                        "Retry-After": str(settings.rate_limit_window_seconds),
                        "X-RateLimit-Limit": str(settings.rate_limit_requests),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, settings.rate_limit_requests - request_count)
            )
            return response

        except HTTPException:
            raise
        except Exception:
            # On Redis errors, allow the request through
            return await call_next(request)
