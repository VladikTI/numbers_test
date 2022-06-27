FROM python:3.10-alpine
WORKDIR /code
ENV FLASK_APP=web.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk update
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev python3-dev musl-dev
COPY requirements.txt .
RUN python3 -m pip install --upgrade -r requirements.txt
EXPOSE 5000
COPY src/ .
CMD sh ./run.sh
# run.sh будет запускать скрипты