FROM andimajore/biocyper_base:python3.10 as setup-stage

WORKDIR /usr/app/
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install
COPY . ./

RUN python3 create_knowledge_graph_docker.py

FROM neo4j:4.4-enterprise as deploy-stage
COPY --from=setup-stage /usr/app/biocypher-out/ /var/lib/neo4j/import/
COPY docker/* ./
RUN cat biocypher_entrypoint_patch.sh | cat - /startup/docker-entrypoint.sh > docker-entrypoint.sh && mv docker-entrypoint.sh /startup/ && chmod +x /startup/docker-entrypoint.sh
