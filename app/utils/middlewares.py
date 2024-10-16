from starlette.middleware.base import BaseHTTPMiddleware

class CreateStateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Example: Set some state or process request before going to route handler
        request.state.user_id = None  # Example state setting
        response = await call_next(request)
        # You can also modify the response after it goes through the route handler
        return response