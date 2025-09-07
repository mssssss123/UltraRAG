FROM nvidia/cuda:12.2.2-base-ubuntu22.04

ENV PATH="/opt/miniconda/bin:$PATH"

RUN apt-get update
RUN apt-get install -y --no-install-recommends bzip2 ca-certificates curl git
RUN update-ca-certificates
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /opt
ADD https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh /opt/miniconda.sh

WORKDIR /ultrarag
COPY . .

RUN chmod +x /opt/miniconda.sh
RUN /opt/miniconda.sh -b -p /opt/miniconda 
RUN rm -f /opt/miniconda.sh 

RUN conda --version && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda env create -f environment.yml
ENV PATH="/opt/miniconda/envs/ultrarag/bin:$PATH"
RUN python -m ensurepip 
RUN pip install uv
RUN uv pip install -e . --system

CMD ["ultrarag", "run", "examples/sayhello.yaml"]