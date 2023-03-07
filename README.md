# BioCypher project template
A quick way to set up a BioCypher-driven knowledge graph pipeline.

## ⚙️ Installation (local, for docker see below)
1. Clone this repository and rename to your project name.
```{bash}
git clone https://github.com/saezlab/biocypher-project-template.git
mv biocypher-project-template my-project
cd my-project
```
2. Make the repository your own.
```{bash}
rm -rf .git
git init
git add .
git commit -m "Initial commit"
# (you can add your remote repository here)
```
3. Install the dependencies using [Poetry](https://python-poetry.org/). (Or feel
free to use your own dependency management system. We provide a `pyproject.toml`
to define dependencies.)
```{bash}
poetry install
```
4. You are ready to go!
```{bash}
poetry shell
python create_knowledge_graph.py
```

## 🛠 Usage

The above command will create a knowledge graph from the example data included
in this repository (borrowed from the [BioCypher
tutorial](https://biocypher.org/tutorial.html)). To do that, it uses the
following components:
- `create_knowledge_graph.py`: the main script that orchestrates the pipeline.
It brings together the BioCypher package with the data sources. To build a 
knowledge graph, you need at least one adapter (see below). For common 
resources, there may already be an adapter available in the BioCypher package or
in a separate repository. You can also write your own adapter, should none be
available for your data.
- `adapter.py`: a module that defines the adapter to the data source. In this
case, it is a random generator script.
- `schema_config.yaml`: a configuration file (found in the `config` directory)
that defines the schema of the knowledge graph. It is used by BioCypher to map
the data source to the knowledge representation on the basis of ontology (see
[this part of the BioCypher 
tutorial](https://biocypher.org/tutorial-ontology.html)).
- `biocypher_config.yaml`: a configuration file (found in the `config` 
directory) that defines some BioCypher parameters, such as the mode, the 
separators used, and other options. It is not strictly necessary; you can pass
settings to the driver at instantiation (in `create_knowledge_graph.py`), or
just use the default settings.

## 🐳 Docker

This repo also contains a `docker compose` workflow to create the example
database using BioCypher and load it into a dockerised Neo4j instance
automatically. To run it, simply execute `docker compose up -d` in the root 
directory of the project. This will start up a single (detached) docker
container with a Neo4j instance that contains the knowledge graph built by
BioCypher as the DB `docker`, which you can connect to and browse at 
localhost:7474 (don't forget to switch the DB to `docker` instead of the 
standard `neo4j`). Authentication is set to `neo4j/neo4jpassword` by default
and can be modified in the `docker_variables.env` file.
