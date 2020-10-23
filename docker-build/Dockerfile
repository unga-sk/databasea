FROM ubuntu:20.04 AS base

ARG databasea_version

RUN apt-get update && \
apt-get install -y python3 python3-pip curl libpq-dev freetds-dev

RUN curl https://codeload.github.com/pymssql/pymssql/tar.gz/2.1.4 -o pymssql.tar.gz
RUN mkdir /pymssql && tar -xzvf pymssql.tar.gz -C /pymssql --strip-components=1
RUN cd pymssql $$ python3 setup.py install


RUN curl "https://codeload.github.com/unga-sk/databasea/tar.gz/${databasea_version}" -o databasea.tar.gz
RUN mkdir /databasea && tar -xzvf databasea.tar.gz -C /databasea --strip-components=1
RUN pip3 install --upgrade cython
RUN cd databasea && pip3 install $(grep -ivE "pymssql" requirements.txt) && python3 setup.py install

ENTRYPOINT [ "patch_database.py", "-y" ]

RUN mkdir /data
RUN useradd runner
RUN chown runner:runner /data

USER runner

WORKDIR /data