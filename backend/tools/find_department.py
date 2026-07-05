"""Deterministic department routing for supported civic issue types."""

from backend.models.schemas import DepartmentInfo


_DEFAULT_DEPARTMENT = (
    "Citizen Services Department",
    "helpdesk@civicai.com",
)

_DEPARTMENT_BY_ISSUE_TYPE: dict[str, tuple[str, str]] = {
    "pothole": (
        "Roads and Public Works Department",
        "roads@civicai.com",
    ),
    "garbage": (
        "Sanitation and Waste Management Department",
        "sanitation@civicai.com",
    ),
    "water leakage": (
        "Water Supply Department",
        "water@civicai.com",
    ),
    "broken street light": (
        "Street Lighting and Electrical Department",
        "streetlights@civicai.com",
    ),
    "fallen tree": (
        "Parks and Urban Forestry Department",
        "parks@civicai.com",
    ),
    "damaged footpath": (
        "Roads and Public Works Department",
        "roads@civicai.com",
    ),
    "illegal dumping": (
        "Sanitation and Waste Management Department",
        "sanitation@civicai.com",
    ),
    "others": _DEFAULT_DEPARTMENT,
}


def find_department(issue_type: str) -> DepartmentInfo:
    """Return the municipal department responsible for an issue type.

    Matching is case-insensitive and ignores surrounding whitespace so callers
    can safely pass user- or model-produced labels. Supported issue types are
    resolved through a fixed in-memory mapping. Unknown, blank, and ``Others``
    labels are routed to the default Citizen Services Department.

    The function performs no network access, AI inference, random selection,
    or environment-dependent lookup, making its result fully deterministic.
    A new ``DepartmentInfo`` instance is returned on every call.

    Args:
        issue_type: Civic issue category to route.

    Returns:
        Contact information for the mapped or default municipal department.
    """
    normalized_issue_type = issue_type.strip().casefold()
    department_name, email = _DEPARTMENT_BY_ISSUE_TYPE.get(
        normalized_issue_type,
        _DEFAULT_DEPARTMENT,
    )
    return DepartmentInfo(
        department_name=department_name,
        email=email,
    )
