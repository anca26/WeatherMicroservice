import os
import grpc
from dotenv import load_dotenv

load_dotenv()
GRPC_API_KEY = os.getenv("GRPC_API_KEY")


# gRPC Interceptor for API key authentication
class ApiKeyInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        md = dict(handler_call_details.invocation_metadata or [])
        if md.get("x-api-key") != GRPC_API_KEY:
            def deny(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid API key")
            return grpc.unary_unary_rpc_method_handler(deny)
        return continuation(handler_call_details)