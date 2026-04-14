# 1. Use Python as our "engine"
FROM python:3.11-slim

# 2. Set the "room" we are working in
WORKDIR /app

# 3. pyzbar for barcode scanning
RUN apt-get update && apt-get install -y libzbar0

# 4. Copy our "recipe list" into the room
COPY requirements.txt .

# 5. Install all the tools on our list
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all our code files into the room
COPY . .

# 7. Tell the playhouse to start the Django project
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
