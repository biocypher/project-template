import biocypher
from adapter import ProteinAdapter, ProteinAdapterFields

# Instantiate the BioCypher driver
# You can use `config/biocypher_config.yaml` to configure the driver or supply
# settings via parameters below
driver = biocypher.Driver(
            user_schema_config_path="config/schema_config.yaml",
            skip_bad_relationships=True,    # Neo4j admin import option
            skip_duplicate_nodes=True,      # Neo4j admin import option
        )

# Choose protein adapter fields to include in the knowledge graph.
# These are defined in the adapter (`adapter.py`).
protein_fields = [
    ProteinAdapterFields.ID,
    ProteinAdapterFields.SEQUENCE,
    ProteinAdapterFields.DESCRIPTION,
    ProteinAdapterFields.TAXON
]

# Create a protein adapter instance
adapter = ProteinAdapter(fields = protein_fields)

# Create a knowledge graph from the adapter
nodes = adapter.get_nodes()
driver.write_nodes(adapter.get_nodes())
