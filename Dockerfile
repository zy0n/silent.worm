### base
FROM debian as base
ENV DEBIAN_FRONTEND=noninteractive

# RUN apt update && apt install -y --no-install-recommends build-essential netcat python3 && rm -rf /var/lib/apt/lists/*
# Install required packages
RUN apt-get update && apt-get upgrade && apt-get dist-upgrade
RUN apt-get install -y \
  docker.io \
  curl \
  libssl-dev \
  libffi-dev 
RUN apt-get install -y  python3-dev 
RUN apt-get install -y  python3-full 
RUN apt-get install -y  python3-venv 
RUN apt-get install -y  python3-pip 
RUN apt-get install -y  build-essential
RUN apt-get install -y  libopencv-core-dev 
RUN apt-get install -y  libopencv-highgui-dev 
RUN apt-get install -y  libopencv-imgproc-dev 
RUN apt-get install -y  libopencv-video-dev 
RUN apt-get install -y  libgtk2.0-dev 
RUN apt-get install -y  libavcodec-dev 
RUN apt-get install -y  libavformat-dev 
RUN apt-get install -y  libswscale-dev 
RUN apt-get install -y  libglib2.0-0 
RUN apt-get install -y  libgl1-mesa-glx
FROM base as playground

# Set the working directory
WORKDIR /home/worm-playground

RUN mkdir -p memory

# Install the latest version of Python and create a virtual environment
RUN python3 -m venv memory/myenv
RUN ln -s /home/worm-playground/memory/myenv/bin/python /usr/local/bin/ai-python
RUN ln -s /home/worm-playground/memory/myenv/bin/pip /usr/local/bin/ai-pip
RUN ldconfig
# Activate the virtual environment
# RUN pip install --trusted-host pypi.python.org pyautogen docker python-dotenv
# Example: You can download your application here
COPY silent /home/worm-playground/silent
COPY .env /home/worm-playground
COPY docker/start.sh /home/worm-playground
# COPY docker/brain.sh /home/worm-playground # not working rn?
COPY requirements.txt /home/worm-playground/

# RUN chmod +x /home/worm-playground/start.sh
# RUN source start.sh

# CMD [ "source /home/worm-playground/start.sh" ]