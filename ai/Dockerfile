FROM python:3.11.9-slim



# Set the environment variable to unbuffered mode to see output logs in real-time
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the requirements file to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
# Copy the application source code to the container
COPY . /app

ENV MONGO_DB_URI=mongodb+srv://navapols:mNTv4yxxXfekI5xe@atlascluster.bc0euhx.mongodb.net/AI_Chat?retryWrites=true&w=majority&appName=AtlasCluster
# Google API Key
ENV MODEL_API_KEY=AIzaSyD0E0og-OPYR2fdp0rcgzuGOBBwBr-5Vo0 
ENV LANGFUSE_PUBLIC_KEY=pk-lf-f6ecc748-b229-40dd-83c3-59b93bac37ab
ENV LANGFUSE_SECRET_KEY=sk-lf-80ea0b82-a340-41a3-b724-62e566237259
ENV Signature_Endpoint=https://backend-ke5m6qbmkq-as.a.run.app
ENV PORT=8080

EXPOSE 8080
# IMPORTANT
# This is the port that FastAPI will be listening on inside the container


# Healthcheck to monitor the application
HEALTHCHECK CMD ["curl", "--fail", "http://localhost:8080", "||", "exit 1"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
