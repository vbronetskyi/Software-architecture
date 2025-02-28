## Services Overview

- **facade-service**  
  - Receives POST and GET requests from the client.
  - For POST requests: Generates a UUID and sends the message to logging-service via gRPC with a retry mechanism.
  - For GET requests: Aggregates messages from logging-service (via HTTP) and messages-service.

- **logging-service**  
  - Stores all received messages in memory (using a dictionary).
  - Implements deduplication (ensuring exactly once delivery) so duplicate messages are ignored.
  - Provides a gRPC endpoint for logging messages (port 50051) and an HTTP endpoint (port 8001) to retrieve stored messages.

- **messages-service**  
  - Acts as a placeholder that returns a static message (e.g., "not implemented yet").

## Requirements

- Docker and Docker Compose.
- Python 3.9 (for local testing).

## Running the Application

1. **Clone the repository.**
2. **Navigate to the repository root directory.**
3. **Build and run all containers:**
   ```bash
   docker-compose up --build
   ```
   This command will build and start all three services.

## Testing with Postman

- **POST Request:**  
  Send a POST request to:
  ```
  http://localhost:8000/message
  ```
  with the following JSON body:
  ```json
  {
    "msg": "msg1"
  }
  ```
  The facade-service will generate a UUID and send the message to logging-service using gRPC. Check the logs to see the retry attempts and deduplication in action.

- **GET Request:**  
  Send a GET request to:
  ```
  http://localhost:8000/messages
  ```
  This will retrieve and return the concatenated messages from logging-service and the static message from messages-service.

## Notes

- Results provited in dit results/  
- The gRPC server in logging-service runs on port 50051.
- The HTTP GET endpoint for retrieving messages in logging-service is available on port 8001.
- Logging in the console shows the retry mechanism and deduplication behavior.

---

This README should help you get started with the project and test its functionality using Postman (my case)
