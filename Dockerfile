FROM ubuntu
RUN apt update
RUN apt install -y python3 python3-pip
COPY app /opt/app
COPY requirements.txt /opt/requirements.txt
WORKDIR /opt
RUN pip3 install -r requirements.txt
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN flask init-db
ENV FLASK_APP=app
CMD flask run --host=0.0.0.0
