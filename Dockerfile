FROM andimajore/miniconda3_kinetic as setup-stage

WORKDIR /usr/

RUN apt update && apt upgrade -y
RUN apt install -y curl libcurl4-openssl-dev libssl-dev python3.10-dev libnss3 libnss3-dev build-essential rsync

RUN conda install python=3.10
RUN pip install --upgrade pip wheel setuptools

RUN wget https://download.java.net/java/GA/jdk15.0.1/51f4f36ad4ef43e39d0dfdbaf6549e32/9/GPL/openjdk-15.0.1_linux-x64_bin.tar.gz
RUN tar -xzf openjdk-15.0.1_linux-x64_bin.tar.gz
RUN rm openjdk-15.0.1_linux-x64_bin.tar.gz
ENV JAVA_HOME=/usr/jdk-15.0.1

RUN pip install poetry

WORKDIR /usr/app/

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install
COPY . ./

RUN python3 create_knowledge_graph_docker.py


FROM neo4j:4.4-enterprise as import-stage
COPY --from=setup-stage /usr/app/biocypher-out/ /var/lib/neo4j/import/
COPY docker/* ./
RUN cat biocypher_entrypoint_patch.sh | cat - /startup/docker-entrypoint.sh > docker-entrypoint.sh && mv docker-entrypoint.sh /startup/ && chmod +x /startup/docker-entrypoint.sh
