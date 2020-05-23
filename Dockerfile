FROM continuumio/miniconda3
LABEL maintainer="Brian Wilson <brian@wildsong.biz>"
LABEL version="1.0"
LABEL biz.wildsong.name="webforms"

ENV WEBFORMS_BASE /srv/webforms
RUN mkdir $WEBFORMS_BASE

COPY requirements.txt ./

# This will upgrade conda, so the fact that the base image is old does not matter
# flask-bootstrap needs hugo
#
RUN conda config --add channels conda-forge &&\
    conda config --add channels hugo &&\
    conda config --add channels Esri &&\
    conda install --file requirements.txt

WORKDIR $WEBFORMS_BASE

COPY start_app.py .
COPY config.py .
COPY app/ app/

EXPOSE 5000
CMD python3 start_app.py 5000
