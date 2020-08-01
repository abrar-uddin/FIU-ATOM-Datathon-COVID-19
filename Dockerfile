FROM python:3.8

WORKDIR /usr/src/app

RUN apt-get update &&\ 
apt-get install proj-bin -y &&\
apt-get install libproj-dev &&\
apt-get install build-essential &&\
apt-get install git

COPY geos ./geos
WORKDIR /usr/src/app/geos
RUN ./autogen.sh &&\
  ./configure &&\
   make &&\
    make install

RUN /sbin/ldconfig -v
RUN pip install --upgrade pip
COPY prereq.txt ./
RUN pip install --no-cache-dir -r prereq.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

COPY . .

WORKDIR /usr/src/app/code

# cmd to launch code when container is run
#EXPOSE 8501
CMD streamlit run dashboard.py --server.port $PORT
#--server.port $PORT

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'