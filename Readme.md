# Code Review Agent
- Application that analyzes GitHub pull requests using a FastAPI API. It leverages Celery for asynchronous task processing, Redis as a message broker, and Currently integrated with **GROQ** with LLM API for code analysis. 
---
## Features Implemented

- Asynchronous processing of code review tasks with Celery
- Integration with GitHub to fetch pull request details
- GROQ LLM API integration for code review analysis
- Result Caching 
- Rate limiting 
- Structured logging 
- Multi-language support
## Project Setup
### Prerequisites

- **Python**: 3.10
- **Redis**: For task management and caching
- **GitHub API Token**: Required for accessing private GitHub repositories
- **LLM API Key**: Required for integrating with the language model (e.g., Groq API)

#### 1. Clone the Repository & Create a Virtual Env
#### 2. Install Dependencies 
         pip install -r requirements.txt
#### 2. Set Up Environment Variables 
         LLM_API_KEY=llm_api_key
         MODEL_NAME=MODEL_NAME
         REDIS_URL=redis://localhost:6379/0
         BROKER_URL=redis://localhost:6379/0
         BACKEND_URL=redis://localhost:6379/0
#### 3. Run the FastAPI Server
         uvicorn main:app --reload   or   python main.py
         The API will be available at http://localhost:8000.
#### 4. Run Celery Wroker
         celery -A celery_app.celery_app worker --loglevel=info
---
## API Documentation
- **Endpoints**
     - **POST /analyze-pr**: Initiates a code review task for a specified GitHub pull request.
       - **Request Body**:
            - **repo_url (str)**: URL of the GitHub repository.
            - **pr_number (str)**: Pull request number.
            - **github_token (str, optional)**: GitHub API token for authentication.
       - **Response**: 
            - Returns a task ID for the initiated review task.

     - **GET /status/{task_id}**: Checks the status of a code review task.
          - Path Parameter:
               - task_id (str): ID of the task.
          - Response: Status of the task (pending, completed, or failed).
     - **GET /results/{task_id}**: Retrieves the results of a completed code review task.
---
## Design Decisions
   - **Asynchronous Processing with Celery**: Using Celery enables handling long-running tasks (like fetching and analyzing PRs) asynchronously, improving API responsiveness and enabling efficient background processing.
   - **Redis for Task Management and Caching**: Redis serves as both the Celery message broker and a caching layer for task results. 
   - **Structured Logging**: JSON-based structured logging is implemented to make logs machine-readable and easier to parse for monitoring or debugging purposes. This helps maintain high observability.
   - **Rate Limiting with SlowAPI**: SlowAPI middleware is used to prevent abuse by limiting the number of requests per minute per client IP. This helps in managing load and preventing excessive use of resources.
---
## Future Improvements
   - **Database for Persistent Storage**: Currently, Redis is used for caching task results. Adding a database (e.g., PostgreSQL) could provide persistent storage for task history and user interactions.
Authentication and Authorization:

   - **Authentication** (e.g., JWT tokens) to protect certain endpoints, especially if deployed in a production environment where users may need restricted access.
   - **Webhooks for Real-Time PR Analysis**: Implement GitHub webhooks to trigger analysis automatically when a new pull request is created, updated, or merged, providing real-time insights.
