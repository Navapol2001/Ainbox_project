FROM python:3.11.9-slim



# Set the environment variable to unbuffered mode to see output logs in real-time
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip
# Copy the requirements file to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
# Copy the application source code to the container
COPY . /app

# Load environment variables from .env file
ENV $(cat .env | xargs)

EXPOSE 8080
# IMPORTANT
# This is the port that FastAPI will be listening on inside the container


# Healthcheck to monitor the application
HEALTHCHECK CMD ["curl", "--fail", "http://localhost:8080", "||", "exit 1"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
