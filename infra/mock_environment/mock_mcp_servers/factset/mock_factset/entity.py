"""``FactSet_EntityReference``: company identity, hierarchy and profile for up to 50 ids."""

from __future__ import annotations

from mockmcp import Tool
from mockmcp.tool import CallContext

from .common import REQUEST_ID_SCHEMA, FactsetData, Issues, check_request_id, choice, id_list

MAX_IDS = 50
FIELDS = (
    "fsymId", "entityProperName", "fsymEntityId", "ultimateParentId", "ultimateParentName", "creditParentId",
    "parentEquityId", "privateEntityFlag", "publicEntityFlag", "securityType", "website", "incorporationDate",
    "countryOfRisk", "countryOfRiskGeoRev", "incorporationCountry", "businessDescription", "phone",
    "headquartersStreet", "headquartersCity", "headquartersState", "headquartersZip", "headquartersCountry",
    "emailIR", "websiteIR", "requestId", "rbicsEconomyClassification", "rbicsSectorClassification",
    "rbicsSubsectorClassification", "rbicsIndustryGroupClassification",
)


class FactsetEntityReference(Tool):
    name = "FactSet_EntityReference"
    title = "FactSet entity reference"
    description = (
        "Validate company identity: entity and parent ids, security id, profile, headquarters and RBICS "
        f"classification. data_type: 'entity_reference'. ids: up to {MAX_IDS} identifiers "
        "(ticker-region such as 'NVDA-US', FactSet ids, ISIN or CUSIP)."
    )
    validate_args = False
    input_schema = {
        "type": "object",
        "properties": {
            "data_type": {"type": "string", "enum": ["entity_reference"]},
            "ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": MAX_IDS},
            "request_id": REQUEST_ID_SCHEMA,
        },
        "required": ["data_type", "ids"],
    }

    def __init__(self, data: FactsetData) -> None:
        self.data = data

    def run(self, args: dict, ctx: CallContext) -> dict:
        issues = Issues()
        check_request_id(issues, args)
        if args.get("data_type") is None:
            issues.add("data_type is required: 'entity_reference'")
        else:
            choice(issues, args, "data_type", ["entity_reference"])
        ids = id_list(issues, args, MAX_IDS)
        issues.raise_if_any()
        return {"data": [self._row(i) for i in ids]}

    def _row(self, identifier: str) -> dict:
        view = self.data.resolve(identifier)
        if view is None:
            return {key: (identifier if key == "requestId" else None) for key in FIELDS}
        profile = self.data.store.view("entity_reference")["entities"].get(f"{view.company.ticker}-US")
        profile = profile or _generated(view.company)
        return {key: (identifier if key == "requestId" else profile.get(key)) for key in FIELDS}


def _generated(company) -> dict:
    """Minimal profile for a universe company without an authored row."""
    rbics = company.rbics or {}
    return {
        "fsymId": company.fsym_entity_id, "entityProperName": company.name, "fsymEntityId": company.fsym_entity_id,
        "ultimateParentId": company.fsym_entity_id, "ultimateParentName": company.name,
        "creditParentId": company.fsym_entity_id, "parentEquityId": company.fsym_security_id,
        "privateEntityFlag": 0, "publicEntityFlag": 1, "securityType": "SHARE", "countryOfRisk": "US",
        "countryOfRiskGeoRev": "US", "incorporationCountry": "US", "headquartersCountry": "US",
        "rbicsEconomyClassification": rbics.get("economy"), "rbicsSectorClassification": rbics.get("sector"),
        "rbicsSubsectorClassification": rbics.get("subsector"),
        "rbicsIndustryGroupClassification": rbics.get("industry_group"),
    }
