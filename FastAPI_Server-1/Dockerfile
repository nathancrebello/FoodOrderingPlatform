FROM python:3.11-slim

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/usr/src/app


RUN apt-get update && apt-get install -y netcat-traditional

# Install Poetry
RUN pip install poetry

# Copy only the necessary files for Poetry
COPY pyproject.toml .
COPY poetry.lock .
COPY requirements.txt .

# Export the dependencies to a requirements.txt file
# RUN poetry export -f requirements.txt --output requirements.txt

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir -p /static /media

# copy entrypoint.sh
COPY ./app/entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]