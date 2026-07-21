from fastapi import HTTPException, Request, status

from app.core.redis import get_redis

MAX_SUBMISSIONS = 10
SUBMISSION_WINDOW_SECONDS = 15 * 60


def client_ip(request: Request) -> str:
    if request.client:
        return request.client.host
    return "unknown"


async def limit_submissions(request: Request, scope: str) -> None:
    """Simple protection of public forms against automated submissions
    (PRD section 10.7): sliding counter per client IP and scope."""
    key = f"submissions:{scope}:{client_ip(request)}"
    redis = get_redis()
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, SUBMISSION_WINDOW_SECONDS)
    if count > MAX_SUBMISSIONS:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Trop de soumissions. Réessayez plus tard."
        )
