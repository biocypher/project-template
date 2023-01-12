import biocypher
from adapter import (
    ExampleAdapter,
    ExampleAdapterNodeType,
    ExampleAdapterEdgeType,
    ExampleAdapterProteinField,
    ExampleAdapterDiseaseField,
)

# Instantiate the BioCypher driver
# You can use `config/biocypher_config.yaml` to configure the driver or supply
# settings via parameters below
driver = biocypher.Driver(
    user_schema_config_path="config/schema_config.yaml",
    skip_bad_relationships=True,  # Neo4j admin import option
    skip_duplicate_nodes=True,  # Neo4j admin import option
)

# Take a look at the ontology structure of the KG according to the schema
driver.show_ontology_structure()

# Choose node types to include in the knowledge graph.
# These are defined in the adapter (`adapter.py`).
node_types = [
    ExampleAdapterNodeType.PROTEIN,
    ExampleAdapterNodeType.DISEASE,
]

# Choose protein adapter fields to include in the knowledge graph.
# These are defined in the adapter (`adapter.py`).
node_fields = [
    # Proteins
    ExampleAdapterProteinField.ID,
    ExampleAdapterProteinField.SEQUENCE,
    ExampleAdapterProteinField.DESCRIPTION,
    ExampleAdapterProteinField.TAXON,
    # Diseases
    ExampleAdapterDiseaseField.ID,
    ExampleAdapterDiseaseField.NAME,
    ExampleAdapterDiseaseField.DESCRIPTION,
]

edge_types = [
    ExampleAdapterEdgeType.PROTEIN_PROTEIN_INTERACTION,
    ExampleAdapterEdgeType.PROTEIN_DISEASE_ASSOCIATION,
]

# Create a protein adapter instance
adapter = ExampleAdapter(
    node_types=node_types,
    node_fields=node_fields,
    edge_types=edge_types,
    # we can leave edge fields empty, defaulting to all fields in the adapter
)


# Create a knowledge graph from the adapter
driver.write_nodes(adapter.get_nodes())
driver.write_edges(adapter.get_edges())

# Write admin import statement
driver.write_import_call()

# Check output
driver.log_duplicates()
driver.log_missing_bl_types()
