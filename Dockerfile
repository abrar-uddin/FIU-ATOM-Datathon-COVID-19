FROM continuumio/miniconda3
RUN conda update --update-all
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

# Pull the environment name out of the environment.yml
RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH
  
WORKDIR /usr/src/app

COPY . .

WORKDIR /usr/src/app/code

# cmd to launch code when container is run
EXPOSE 8501
RUN pip install streamlit && conda install geopandas && conda install geoplot -c conda-forge && conda install seaborn &&\
conda install plotly
CMD streamlit run dashboard.py
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