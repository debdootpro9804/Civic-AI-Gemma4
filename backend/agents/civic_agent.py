"""LangGraph orchestration for the CivicAI reporting workflow."""

from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.models.schemas import (
    CitizenDetails,
    CivicAgentResult,
    Complaint,
    DepartmentInfo,
    ImageAnalysisResult,
)
from backend.services.gemma_service import GemmaService
from backend.tools import find_department, generate_complaint
from backend.tools.create_report import create_report

class _CivicAgentState(TypedDict):
    """Internal state accumulated while the CivicAgent graph executes."""

    citizen_details: CitizenDetails
    image_bytes: bytes
    image_analysis: NotRequired[ImageAnalysisResult]
    department: NotRequired[DepartmentInfo]
    complaint: NotRequired[Complaint]
    pdf_path: NotRequired[str]


class CivicAgent:
    """Orchestrate CivicAI analysis, routing, and complaint generation.

    The agent owns only workflow sequencing. Each graph node delegates its
    operation to an existing service or tool, preserving those components as
    the single source of business and model behavior.
    """

    def __init__(self, gemma_service: GemmaService | None = None) -> None:
        """Initialize the agent and compile its linear LangGraph workflow.

        Args:
            gemma_service: Optional service instance for dependency injection.
                A default ``GemmaService`` is created when one is not provided.
        """
        self._gemma_service = gemma_service or GemmaService()
        self._graph = self._build_graph()

    def run(
        self,
        citizen_name: str,
        contact_number: str,
        location: str,
        image_bytes: bytes,
    ) -> CivicAgentResult:
        """Execute the complete civic reporting workflow.

        Args:
            citizen_name: Full name of the reporting citizen.
            contact_number: Citizen's contact number for follow-up.
            location: Location where the civic issue was observed.
            image_bytes: Raw bytes of the uploaded issue image.

        Returns:
            One structured result containing the citizen details, image
            analysis, responsible department, and generated complaint.
        """
        citizen_details = CitizenDetails(
            full_name=citizen_name,
            contact_number=contact_number,
            location=location,
        )
        final_state = self._graph.invoke(
            {
                "citizen_details": citizen_details,
                "image_bytes": image_bytes,
            }
        )

        return CivicAgentResult(
            citizen_details=final_state["citizen_details"],
            image_analysis=final_state["image_analysis"],
            department=final_state["department"],
            complaint=final_state["complaint"],
            pdf_path=final_state["pdf_path"],
        )

    def _analyze(self, state: _CivicAgentState) -> dict[str, ImageAnalysisResult]:
        """Run image analysis and add its structured result to graph state."""
        return {
            "image_analysis": self._gemma_service.analyze_image(
                state["image_bytes"]
            )
        }

    @staticmethod
    def _find_department(
        state: _CivicAgentState,
    ) -> dict[str, DepartmentInfo]:
        """Resolve the responsible department from the analyzed issue type."""
        return {
            "department": find_department(
                state["image_analysis"].issue_type
            )
        }

    @staticmethod
    def _generate_complaint(
        state: _CivicAgentState,
    ) -> dict[str, Complaint]:
        """Generate a complaint from the accumulated workflow state."""
        citizen = state["citizen_details"]
        return {
            "complaint": generate_complaint(
                citizen_name=citizen.full_name,
                contact_number=citizen.contact_number,
                location=citizen.location,
                image_analysis=state["image_analysis"],
                department=state["department"],
            )
        }
    @staticmethod
    def _create_report(state: _CivicAgentState,) -> dict[str, str]:
        """Generate a PDF report from the accumulated workflow state."""
        pdf_path = create_report(
        citizen_details=state["citizen_details"],
        image_analysis=state["image_analysis"],
        department=state["department"],
        complaint=state["complaint"],
    )

        return {
        "pdf_path": pdf_path,
        }

    def _build_graph(self):
        """Build and compile the linear CivicAI workflow graph."""
        graph = StateGraph(_CivicAgentState)
        graph.add_node("Analyze", self._analyze)
        graph.add_node("Department", self._find_department)
        graph.add_node("Complaint", self._generate_complaint)
        graph.add_node("Report", self._create_report) 
        graph.add_edge(START, "Analyze")
        graph.add_edge("Analyze", "Department")
        graph.add_edge("Department", "Complaint")
        graph.add_edge("Complaint", "Report")
        graph.add_edge("Report", END)

        return graph.compile()
