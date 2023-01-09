FROM fission/python-env-3.10
COPY ./fission.py ./server.py


RUN apk add curl
RUN apk add libaio
RUN apk add gcompat
RUN ln -s /usr/lib/libnsl.so.2 /usr/lib/libnsl.so.1
RUN ln -s /lib/libc.musl-x86_64.so.1 /usr/lib/libresolv.so.2
RUN curl -OL https://download.oracle.com/otn_software/linux/instantclient/19600/instantclient-basic-linux.x64-19.6.0.0.0dbru.zip
RUN unzip instantclient-basic-linux.x64-19.6.0.0.0dbru.zip
RUN rm -rf instantclient-basic-linux.x64-19.6.0.0.0dbru.zip
RUN mv instantclient_19_6 /opt/instantclient
RUN cp -r /opt/instantclient/* /lib/
ENV LD_LIBRARY_PATH=/opt/instantclient


RUN mkdir -p /opt/envs/etria.lionx.com.br
RUN touch /opt/envs/etria.lionx.com.br/.env

RUN mkdir -p /opt/envs/heimdall.lionx.com.br
RUN touch /opt/envs/heimdall.lionx.com.br/.env

RUN mkdir -p /opt/envs/persephone.client.python.lionx.com.br
RUN touch /opt/envs/persephone.client.python.lionx.com.br/.env


COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./func ./func
