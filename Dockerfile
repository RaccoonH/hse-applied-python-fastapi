FROM python:3.9

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x run_app.sh
RUN chmod a+x run_app_in_one_container.sh

RUN apt-get update && apt-get install -y redis-server

CMD [ "./run_app_in_one_container.sh" ]
