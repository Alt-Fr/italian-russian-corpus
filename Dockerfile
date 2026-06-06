FROM python:3.12-slim
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y netcat-openbsd

     
COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
   
