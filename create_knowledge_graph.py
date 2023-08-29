from biocypher import BioCypher
from igan.adapters.clinicaltrials_adapter import (
    ClinicalTrialsAdapter,
    QUERY_PARAMS,
)

bc = BioCypher(
    biocypher_config_path="config/biocypher_config.yaml",
)
adapter = ClinicalTrialsAdapter()

bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

bc.write_import_call()
bc.summary()
