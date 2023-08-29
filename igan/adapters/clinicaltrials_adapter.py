import random
import string
from enum import Enum, auto
from itertools import chain
from typing import Optional
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")

import requests

QUERY_PARAMS = {
    "format": "json",
    "query.parser": "advanced",
    "query.cond": "iga nephropathy",
    # "query.term": "AREA[LastUpdatePostDate]RANGE[2023-01-15,MAX]",
    # "query.locn": "",
    # "query.titles": "",
    # "query.intr": "",
    # "query.outc": "",
    # "query.spons": "",
    # "query.lead": "",
    # "query.id": "",
    # "query.patient": "",
    # "filter.overallStatus": ["NOT_YET_RECRUITING", "RECRUITING"],
    # "filter.geo": "",
    # "filter.ids": ["NCT04852770", "NCT01728545", "NCT02109302"],
    # "filter.advanced": "",
    # "filter.synonyms": "",
    # "postFilter.overallStatus": ["NOT_YET_RECRUITING", "RECRUITING"],
    # "postFilter.geo": "",
    # "postFilter.ids": ["NCT04852770", "NCT01728545", "NCT02109302"],
    # "postFilter.advanced": "",
    # "postFilter.synonyms": "",
    # "aggFilters": "",
    # "geoDecay": "",
    # "fields": ["NCTId", "BriefTitle", "OverallStatus", "HasResults"],
    # "sort": ["@relevance"],
    # "countTotal": False,
    # "pageSize": 10,
    # "pageToken": "",
}


class ClinicalTrialsAdapterNodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """

    STUDY = auto()
    ORGANISATION = auto()
    OUTCOME = auto()
    DRUG = auto()
    DISEASE = auto()
    LOCATION = auto()


class ClinicalTrialsAdapterStudyField(Enum):
    """
    Define possible fields the adapter can provide for studies.
    """

    ID = "identificationModule/nctId"
    BRIEF_TITLE = "identificationModule/briefTitle"
    OFFICIAL_TITLE = "identificationModule/officialTitle"
    STATUS = "statusModule/overallStatus"
    BRIEF_SUMMARY = "descriptionModule/briefSummary"
    TYPE = "designModule/studyType"
    ALLOCATION = "designModule/designInfo/allocation"
    PHASES = "designModule/phases"
    MODEL = "designModule/designInfo/interventionModel"
    PRIMARY_PURPOSE = "designModule/designInfo/primaryPurpose"
    NUMBER_OF_PATIENTS = "designModule/enrollmentInfo/count"
    ELIGIBILITY_CRITERIA = "eligibilityModule/eligibilityCriteria"
    HEALTHY_VOLUNTEERS = "eligibilityModule/healthyVolunteers"
    SEX = "eligibilityModule/sex"
    MINIMUM_AGE = "eligibilityModule/minimumAge"
    MAXIMUM_AGE = "eligibilityModule/maximumAge"
    STANDARDISED_AGES = "eligibilityModule/stdAges"


class ClinicalTrialsAdapterDiseaseField(Enum):
    """
    Define possible fields the adapter can provide for diseases.
    """

    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"


class ClinicalTrialsAdapterEdgeType(Enum):
    """
    Enum for the types of the protein adapter.
    """

    STUDY_TO_DRUG = auto()
    STUDY_TO_DISEASE = auto()
    STUDY_TO_LOCATION = auto()


class ClinicalTrialsAdapterProteinProteinEdgeField(Enum):
    """
    Define possible fields the adapter can provide for protein-protein edges.
    """

    INTERACTION_TYPE = "interaction_type"
    INTERACTION_SOURCE = "interaction_source"


class ClinicalTrialsAdapterProteinDiseaseEdgeField(Enum):
    """
    Define possible fields the adapter can provide for protein-disease edges.
    """

    ASSOCIATION_TYPE = "association_type"
    ASSOCIATION_SOURCE = "association_source"


class ClinicalTrialsAdapter:
    """
    ClinicalTrials BioCypher adapter. Generates nodes and edges for creating a
    knowledge graph.

    Args:
        node_types: List of node types to include in the result.
        node_fields: List of node fields to include in the result.
        edge_types: List of edge types to include in the result.
        edge_fields: List of edge fields to include in the result.
    """

    def __init__(
        self,
        node_types: Optional[list] = None,
        node_fields: Optional[list] = None,
        edge_types: Optional[list] = None,
        edge_fields: Optional[list] = None,
    ):
        self._set_types_and_fields(
            node_types, node_fields, edge_types, edge_fields
        )

        self.base_url = "https://clinicaltrials.gov/api/v2"

        self._studies = self._get_studies(QUERY_PARAMS)

        self._preprocess()

    def _get_studies(self, query_params):
        """
        Get all studies fitting the parameters from the API.

        Args:
            query_params: Dictionary of query parameters to pass to the API.

        Returns:
            A list of studies (dictionaries).
        """
        url = f"{self.base_url}/studies"
        response = requests.get(url, params=query_params)
        result = response.json()
        # append pages until empty
        while result.get("nextPageToken"):
            query_params["pageToken"] = result.get("nextPageToken")
            response = requests.get(url, params=query_params)
            result.get("studies").extend(response.json().get("studies"))
            result["nextPageToken"] = response.json().get("nextPageToken")

        return result.get("studies")

    def _preprocess(self):
        """
        Preprocess raw API results into node and edge types.
        """

        self._organisations = {}
        self._outcomes = {}
        self._interventions = {}
        self._diseases = {}
        self._locations = {}

        self._study_to_drug_edges = []
        self._study_to_disease_edges = []
        self._study_to_location_edges = []

        for study in self._studies:
            self._preprocess_study(study)

    def _preprocess_study(self, study: dict):
        if not study.get("protocolSection"):
            return

        try:
            _id = (
                study.get("protocolSection")
                .get("identificationModule")
                .get("nctId")
            )
        except AttributeError:
            _id = None

        if not _id:
            return

        study["nctId"] = _id

        protocol = study.get("protocolSection")
        # the derived module has interesting info about conditions and
        # interventions, linking to MeSH terms; could use for diseases and
        # drugs

        # organisations
        if ClinicalTrialsAdapterNodeType.ORGANISATION in self.node_types:
            try:
                name = (
                    protocol.get("identificationModule")
                    .get("organization")
                    .get("fullName")
                )
            except AttributeError:
                name = None

            try:
                oclass = (
                    protocol.get("identificationModule")
                    .get("organization")
                    .get("class")
                )
            except AttributeError:
                oclass = None

        if name and name not in self._organisations:
            self._organisations.update(
                {
                    name: {"class": oclass or "N/A"},
                }
            )

        # outcomes
        if ClinicalTrialsAdapterNodeType.OUTCOME in self.node_types:
            try:
                primary = protocol.get("outcomesModule").get("primaryOutcomes")
            except AttributeError:
                primary = None

            try:
                secondary = protocol.get("outcomesModule").get(
                    "secondaryOutcomes"
                )
            except AttributeError:
                secondary = None

            if primary:
                for outcome in primary:
                    self._add_outcome(outcome, True)

            if secondary:
                for outcome in secondary:
                    self._add_outcome(outcome, False)

        # drugs
        if ClinicalTrialsAdapterNodeType.DRUG in self.node_types:
            try:
                interventions = protocol.get("armsInterventionsModule").get(
                    "interventions"
                )
            except AttributeError:
                interventions = None

            if interventions:
                for intervention in interventions:
                    try:
                        name = intervention.get("name")
                    except AttributeError:
                        name = None

                    try:
                        intervention_type = intervention.get("type")
                    except AttributeError:
                        intervention_type = None

                    try:
                        description = intervention.get("description")
                        description = replace_quote(description)
                        description = replace_newline(description)
                    except AttributeError:
                        description = None

                    try:
                        mapped_names = intervention.get(
                            "interventionMappedName"
                        )
                    except AttributeError:
                        mapped_names = None

                    if name and name not in self._interventions.keys():
                        self._interventions.update(
                            {
                                name: {
                                    "type": intervention_type or "N/A",
                                    "description": description or "N/A",
                                    "mapped_names": mapped_names or "N/A",
                                },
                            }
                        )

                        # study to drug edges
                        if str(intervention_type).lower() == "drug":
                            self._study_to_drug_edges.append(
                                (
                                    None,
                                    _id,
                                    name,
                                    "study_has_drug",
                                    {"description": description or "N/A"},
                                )
                            )

        # diseases
        if ClinicalTrialsAdapterNodeType.DISEASE in self.node_types:
            try:
                conditions = protocol.get("conditionsModule").get("conditions")
            except AttributeError:
                conditions = None

            try:
                keywords = protocol.get("conditionsModule").get("keywords")
            except AttributeError:
                keywords = []

            if conditions:
                for condition in conditions:
                    if condition not in self._diseases.keys():
                        self._diseases.update(
                            {condition: {"keywords": keywords}}
                        )
                    else:
                        if keywords:
                            if self._diseases[condition]["keywords"]:
                                self._diseases[condition]["keywords"].extend(
                                    keywords
                                )
                            else:
                                self._diseases[condition]["keywords"] = keywords

                    # study to disease edges
                    self._study_to_disease_edges.append(
                        (
                            None,
                            _id,
                            condition,
                            "study_has_disease",
                            {},
                        )
                    )

        # locations
        if ClinicalTrialsAdapterNodeType.LOCATION in self.node_types:
            if not protocol.get("contactsLocationsModule"):
                return  # only works in last position of flow?
            if not protocol.get("contactsLocationsModule").get("locations"):
                return

            for location in protocol.get("contactsLocationsModule").get(
                "locations"
            ):
                try:
                    name = replace_quote(location.get("facility"))
                except AttributeError:
                    name = None

                try:
                    city = replace_quote(location.get("city"))
                except AttributeError:
                    city = None

                try:
                    state = replace_quote(location.get("state"))
                except AttributeError:
                    state = None

                try:
                    country = replace_quote(location.get("country"))
                except AttributeError:
                    country = None

                if name and name not in self._locations.keys():
                    self._locations.update(
                        {
                            name: {
                                "city": city or "N/A",
                                "state": state or "N/A",
                                "country": country or "N/A",
                            },
                        }
                    )

                # study to location edges
                self._study_to_location_edges.append(
                    (
                        None,
                        _id,
                        name,
                        "study_has_location",
                        {},
                    )
                )

    def _add_outcome(self, outcome: dict, primary: bool):
        try:
            measure = outcome.get("measure")
            measure = replace_quote(measure)
        except AttributeError:
            measure = None

        try:
            time_frame = outcome.get("timeFrame")
        except AttributeError:
            time_frame = None

        try:
            description = outcome.get("description")
            description = replace_quote(description)
        except AttributeError:
            description = None

        if measure and measure not in self._outcomes:
            self._outcomes.update(
                {
                    measure: {
                        "primary": primary,
                        "time_frame": time_frame or "N/A",
                        "description": description or "N/A",
                    },
                }
            )

    def get_nodes(self):
        """
        Returns a generator of node tuples for node types specified in the
        adapter constructor.
        """

        logger.info("Generating nodes.")

        self.studies = self._get_studies(QUERY_PARAMS)

        if ClinicalTrialsAdapterNodeType.STUDY in self.node_types:
            for study in self._studies:
                if not study.get("nctId"):
                    continue

                _props = self._get_study_props_from_fields(study)

                yield (study.get("nctId"), "study", _props)

        if ClinicalTrialsAdapterNodeType.ORGANISATION in self.node_types:
            for name, props in self._organisations.items():
                yield (name, "organisation", props)

        if ClinicalTrialsAdapterNodeType.OUTCOME in self.node_types:
            for measure, props in self._outcomes.items():
                yield (measure, "outcome", props)

        if ClinicalTrialsAdapterNodeType.DRUG in self.node_types:
            for name, props in self._interventions.items():
                yield (name, "drug", props)

        if ClinicalTrialsAdapterNodeType.DISEASE in self.node_types:
            for name, props in self._diseases.items():
                yield (name, "disease", props)

        if ClinicalTrialsAdapterNodeType.LOCATION in self.node_types:
            for name, props in self._locations.items():
                yield (name, "location", props)

    def _get_study_props_from_fields(self, study):
        """
        Returns a dictionary of properties for a study node, given the selected
        fields.

        Args:
            study: The study (raw API result) to extract properties from.

        Returns:
            A dictionary of properties.
        """

        props = {}

        for field in self.node_fields:
            if field not in ClinicalTrialsAdapterStudyField:
                continue

            if field == ClinicalTrialsAdapterStudyField.ID:
                continue

            path = field.value.split("/")
            value = study.get("protocolSection")

            if value:
                for step in path:
                    if value:
                        value = value.get(step)

            if isinstance(value, list):
                value = [replace_quote(v) for v in value]
            elif isinstance(value, str):
                value = replace_quote(value)

            props.update({field.name.lower(): value or "N/A"})

        return props

    def get_edges(self):
        """
        Returns a generator of edge tuples for edge types specified in the
        adapter constructor.
        """

        logger.info("Generating edges.")

        if ClinicalTrialsAdapterEdgeType.STUDY_TO_DRUG in self.edge_types:
            yield from self._study_to_drug_edges

        if ClinicalTrialsAdapterEdgeType.STUDY_TO_DISEASE in self.edge_types:
            yield from self._study_to_disease_edges

        if ClinicalTrialsAdapterEdgeType.STUDY_TO_LOCATION in self.edge_types:
            yield from self._study_to_location_edges

    def _set_types_and_fields(
        self, node_types, node_fields, edge_types, edge_fields
    ):
        if node_types:
            self.node_types = node_types
        else:
            self.node_types = [type for type in ClinicalTrialsAdapterNodeType]

        if node_fields:
            self.node_fields = node_fields
        else:
            self.node_fields = [
                field
                for field in chain(
                    ClinicalTrialsAdapterStudyField,
                    ClinicalTrialsAdapterDiseaseField,
                )
            ]

        if edge_types:
            self.edge_types = edge_types
        else:
            self.edge_types = [type for type in ClinicalTrialsAdapterEdgeType]

        if edge_fields:
            self.edge_fields = edge_fields
        else:
            self.edge_fields = [field for field in chain()]


def replace_quote(string):
    return string.replace('"', "'")


def replace_newline(string):
    return string.replace("\n", " | ")
