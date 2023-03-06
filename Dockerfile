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
# RUN python3 scripts/update_import_script.py "/usr/app/biocypher-out/test/neo4j-admin-import-call.sh" "/usr/app/biocypher-out/" "neo4j-admin"


FROM neo4j:4.4-enterprise as import-stage

COPY --from=setup-stage /usr/app/biocypher-out/ /var/lib/neo4j/import/
RUN chmod +x /var/lib/neo4j/import/docker/neo4j-admin-import-call.sh
RUN import/docker/neo4j-admin-import-call.sh
COPY docker/docker-neo4j-entrypoint_biocypher.sh /startup/docker-entrypoint.sh 

COPY docker/create_table.sh ./
# RUN chmod +x create_table.sh
# RUN ./create_table.sh
# RUN echo "bash /var/lib/neo4j/import/docker/neo4j-admin-import-call.sh && bash create_table.sh &" > import/import.sh && chmod +x /startup/docker-entrypoint.sh
RUN echo "bash create_table.sh &" > import/import.sh && chmod +x /startup/docker-entrypoint.sh

CMD ["neo4j"]