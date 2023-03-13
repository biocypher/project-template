from biocypher import BioCypher
from adapter import (
    ExampleAdapter,
    ExampleAdapterNodeType,
    ExampleAdapterEdgeType,
    ExampleAdapterProteinField,
    ExampleAdapterDiseaseField,
)

bc = BioCypher(
    biocypher_config_path="config/biocypher_docker_config.yaml",
)

node_types = [
    ExampleAdapterNodeType.PROTEIN,
    ExampleAdapterNodeType.DISEASE,
]

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

adapter = ExampleAdapter(
    node_types=node_types,
    node_fields=node_fields,
    edge_types=edge_types,
)

bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

bc.write_import_call()

bc.log_duplicates()
bc.log_missing_bl_types()
