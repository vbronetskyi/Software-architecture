import grpc
from concurrent import futures
import time

import logging_pb2
import logging_pb2_grpc

messages = {}

class LoggingServiceServicer(logging_pb2_grpc.LoggingServiceServicer):
    def LogMessage(self, request, context):
        if request.id in messages:
            print(f"Duplicate received: {request.id} -> {request.msg}")
            return logging_pb2.LogReply(status="duplicate")
        messages[request.id] = request.msg
        print(f"Logged message: {request.id} -> {request.msg}")
        return logging_pb2.LogReply(status="saved")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC LoggingService is running on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
