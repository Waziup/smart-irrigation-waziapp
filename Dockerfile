FROM python:slim-buster

# Copy whole folder to container
COPY . /root/src

WORKDIR /root/src

RUN pip3 install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update \
    && apt-get install -y \
    zip \
    curl

RUN cd /root/src/ \
    && zip /index.zip docker-compose.yml package.json


# Make port available
EXPOSE 5000/tcp
#----------------------------#

# Uncomment For development
# ENTRYPOINT ["tail", "-f", "/dev/null"]

# Uncomment For production
ENTRYPOINT ["python3","/root/src/app.py"]