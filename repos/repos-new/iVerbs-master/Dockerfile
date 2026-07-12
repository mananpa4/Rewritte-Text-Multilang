FROM python:3
RUN apt-get update && apt-get -y install --on-install-recommends \
    libfreetype6-dev \
    libportmidi-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "iverb.py"]
