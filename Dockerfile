FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
COPY environment.yml .
# RUN conda update -n base -c defaults conda
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "covid19", "/bin/bash", "-c"]

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
  
WORKDIR /usr/src/app

COPY . .

WORKDIR /usr/src/app/code

# cmd to launch code when container is run
EXPOSE 8501
#RUN pip install streamlit && conda install geopandas && conda install geoplot -c conda-forge && conda install seaborn &&\
#conda install plotly
CMD streamlit run dashboard.py
#--server.port $PORT

