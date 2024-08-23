FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the setup script into the container
COPY setup.sh /app/setup.sh

# Make the setup script executable and run it
RUN chmod +x /app/setup.sh && /app/setup.sh

COPY ./requirements.txt /app/requirements.txt

# Install pip requirements
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app

RUN pip uninstall faiss-cpu bson pymongo -y

RUN pip install faiss-gpu-cu11 pymongo

# Expose the application port
EXPOSE 5000

# Set Flask environment variable
ENV FLASK_APP=app.py 

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
