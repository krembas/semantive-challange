 FROM python:3.6-slim
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /semantive-challange
 WORKDIR /semantive-challange
 ADD requirements.txt /semantive-challange/
 RUN pip install -r requirements.txt
 ADD /. /semantive-challange/
