# set base image (host OS)
FROM python:buster

# set the working directory in the container
WORKDIR /home

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local directory to the working directory
COPY . .

# command to run on container start
CMD [ "bash", "run.sh" ]
