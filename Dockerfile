# Use official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Command to run the app
CMD ["gunicorn", "lunch_decider.wsgi:application", "--bind", "0.0.0.0:8000"]
