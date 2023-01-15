##### building stage #####
FROM python:3.10 as builder

RUN apt-get update && apt-get install -y \
    unzip 

# chrome driver
ADD https://chromedriver.storage.googleapis.com/103.0.5060.24/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chromedriver_linux64.zip && \
    rm -f chromedriver_linux64.zip

# python package
RUN pip install --upgrade pip

##### production stage #####
FROM python:3.10
COPY --from=builder /opt/ /opt/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg

# GET Google Chrome
RUN apt-get install -y wget
RUN apt-get install -y httpie
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# copy all the files to the container
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]


