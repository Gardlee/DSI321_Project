# Use an official Miniconda image as a parent image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN conda install --yes --file requirements.txt psycopg2-binary

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . /app

# Ensure all directories are writable
RUN chmod -R 777 /app
RUN mkdir -p /mlflow && chmod -R 777 /mlflow

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV MLFLOW_BACKEND_URI=postgresql+psycopg2://user:password@postgres:5432/datascience
ENV MLFLOW_ARTIFACT_ROOT=/mlflow

# Run mlflow server when the container launches
CMD ["mlflow", "server", "--backend-store-uri", "${MLFLOW_BACKEND_URI}", "--default-artifact-root", "${MLFLOW_ARTIFACT_ROOT}", "--host", "0.0.0.0", "--port", "5000"]
"--port", "5000"]
