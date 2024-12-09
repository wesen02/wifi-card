FROM python:3.10-slim

WORKDIR /app

COPY main.py requirements.txt .

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN chmod +x /app/main.py

# Add the cron job
RUN echo "59 23 * * * /usr/local/bin/python3 /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job

# Set the correct permissions for the cron job file
RUN chmod 0644 /etc/cron.d/my-cron-job

# Apply the cron job
RUN crontab /etc/cron.d/my-cron-job

# Create a log file for cron
RUN touch /var/log/cron.log

# Start cron and tail the log file
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]