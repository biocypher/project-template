# BioCypher project template
A quick way to set up a BioCypher-driven knowledge graph pipeline.

## Installation
1. Clone this repository and rename to your project name
```{bash}
git clone https://github.com/saezlab/biocypher-project-template.git
mv biocypher-project-template my-project
cd my-project
```
2. Make the repository your own
```{bash}
rm -rf .git
git init
git add .
git commit -m "Initial commit"
```
3. Install the dependencies using [Poetry](https://python-poetry.org/)
```{bash}
poetry install
```
4. You are ready to go!
```{bash}
poetry shell
python create_knowledge_graph.py
```


