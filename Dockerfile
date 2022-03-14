FROM python:slim-buster

COPY . /root/src/

# Added
COPY . /root/app/ 

RUN pip install requests

RUN  apt-get update \
     && apt-get install -y \
     curl \
     zip \
     && cd /root/src/ \
     && zip /index.zip docker-compose.yml package.json

# Only for the sample app in order to have the source code on the host
RUN cd /root/src/ && zip -q -r /index.zip .

#----------------------------#

# Uncomment For development
#ENTRYPOINT ["tail", "-f", "/dev/null"]


# Uncomment For production
ENTRYPOINT ["python", "-u", "/root/src/main.py"]


# Here is how you can access inside your container:
# sudo docker exec -it waziup.smart-irrigation-waziapp sh
# sudo docker exec -it waziup.smart-irrigation-waziapp bash
