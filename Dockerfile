# 使用CUDA基础镜像
FROM nvidia/cuda:12.2.2-base-ubuntu22.04

# 设置 pip 源
ENV PIP_INDEX_URL=${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple/}
# 设置环境变量
ENV PATH="/opt/miniconda/bin:$PATH"

# 设置工作目录
WORKDIR /opt

# 使用 ADD 下载 Miniconda 安装脚本
ADD https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh /opt/miniconda.sh

# 设置工作目录和环境
WORKDIR /ultrarag
COPY . .

# 修改权限并安装 Miniconda # 在conda环境中安装依赖
RUN chmod +x /opt/miniconda.sh && \
    /opt/miniconda.sh -b -p /opt/miniconda && \
    rm -f /opt/miniconda.sh && \
    conda create -n ultrarag python=3.10 -y && \
    echo "conda activate ultrarag" >> ~/.bashrc && \ 
    python -m ensurepip && \
    pip install --no-cache-dir -i $PIP_INDEX_URL -r requirements.txt

# 下载并解压文件
ADD https://github.com/qdrant/qdrant/releases/download/v1.12.5/qdrant-x86_64-unknown-linux-gnu.tar.gz /opt/qdrant.tar.gz
RUN tar -xzf /opt/qdrant.tar.gz -C /opt && \
    rm /opt/qdrant.tar.gz && \
    chmod +x /opt/qdrant

# 启动命令
CMD ["bash", "scripts/run_server.sh"] 