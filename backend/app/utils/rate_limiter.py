import time
import asyncio
from fastapi import HTTPException

class RateLimiter:
    def __init__(self, max_calls, time_frame):
        self.max_calls = max_calls
        self.time_frame = time_frame
        self.calls = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            
            # Remove old calls
            self.calls = [call for call in self.calls if call > now - self.time_frame]
            
            if len(self.calls) >= self.max_calls:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            self.calls.append(now)