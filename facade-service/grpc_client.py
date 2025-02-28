import grpc
import logging_pb2
import logging_pb2_grpc

def send_log_message(msg_id, msg):
    channel = grpc.insecure_channel('logging-service:50051')
    stub = logging_pb2_grpc.LoggingServiceStub(channel)
    request = logging_pb2.LogRequest(id=msg_id, msg=msg)
    response = stub.LogMessage(request, timeout=2)
    return response.status
