FROM python:3-alpine

WORKDIR /work
RUN wget http://gensen.dl.itc.u-tokyo.ac.jp/soft/pytermextract-0_01.zip
RUN unzip pytermextract-0_01.zip
RUN cd pytermextract-0_01 && python setup.py install

RUN apk update
RUN apk --no-cache add git gcc libc-dev libxml2-dev libxslt-dev

RUN git clone https://github.com/fukumasa/auto-create-qiita-tags

WORKDIR /work/auto-create-qiita-tags
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]
EXPOSE 5000
