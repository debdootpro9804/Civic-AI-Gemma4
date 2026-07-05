"""Service boundary for local Gemma model interactions through Ollama."""

import json
import tempfile
from pathlib import Path
from typing import Any

import ollama
from pydantic import ValidationError

from backend.models.schemas import ImageAnalysisResult


class GemmaService:
    """Provide the single entry point for all interactions with the Gemma model.

    This service isolates Ollama request construction, temporary image
    handling, and model response parsing from the rest of the application.
    Callers depend only on the reusable ``ImageAnalysisResult`` contract and
    remain decoupled from the local Gemma runtime.
    """

    _MODEL_NAME = "gemma4:e2b"
    _ANALYSIS_PROMPT = """You are an AI civic inspection assistant.

Return ONLY valid JSON.

Choose ONE issue_type from this list only:

- Pothole
- Garbage
- Water Leakage
- Broken Street Light
- Fallen Tree
- Damaged Footpath
- Illegal Dumping
- Others

description:
One detailed sentence with a clear description of the issue and any relevant details.

confidence: confidence must be a realistic estimate between 0.0 and 0.99.

Return ONLY JSON.

Return exactly one JSON object matching this schema:
{schema}

Return JSON only. Do not use Markdown, code fences, commentary, or additional
keys."""

    def generate_structured_text(
        self,
        prompt: str,
        schema: dict[str, Any],
    ) -> str:
        """Generate schema-constrained text with the local Gemma model.

        This prompt-agnostic service method keeps Ollama communication inside
        ``GemmaService`` while allowing calling tools to own their specialized
        prompt engineering and response validation.

        Args:
            prompt: Complete task instructions prepared by the calling tool.
            schema: JSON schema that the model response must satisfy.

        Returns:
            Raw structured response content produced by Gemma.

        Raises:
            ValueError: If the prompt or schema is empty.
            RuntimeError: If Ollama fails or Gemma returns no content.
        """
        if not prompt.strip():
            raise ValueError("A non-empty prompt is required.")
        if not schema:
            raise ValueError("A non-empty response schema is required.")

        try:
            response = ollama.chat(
                model=self._MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                format=schema,
                options={"temperature": 0},
            )
        except ollama.ResponseError as exc:
            raise RuntimeError(
                f"Ollama failed to generate structured text: {exc.error}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "Unable to communicate with local Ollama. Ensure Ollama is "
                "running and the gemma4:e2b model is installed."
            ) from exc

        content = response.message.content
        if not content:
            raise RuntimeError("Gemma returned an empty structured response.")

        return content

    def analyze_image(self, image_bytes: bytes) -> ImageAnalysisResult:
        """Analyze an image with local Gemma 4 and return a structured result.

        Args:
            image_bytes: Raw bytes of the image to analyze.

        Returns:
            A structured image analysis result.

        Raises:
            ValueError: If the image is empty or is not a supported image type.
            RuntimeError: If Ollama fails, Gemma returns invalid output, or the
                temporary image cannot be removed.
        """
        suffix = self._detect_image_suffix(image_bytes)
        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=suffix,
                delete=False,
            ) as temporary_image:
                temporary_path = Path(temporary_image.name)
                temporary_image.write(image_bytes)

            schema = ImageAnalysisResult.model_json_schema()
            prompt = self._ANALYSIS_PROMPT.format(
                schema=json.dumps(schema, indent=2)
            )

            try:
                response = ollama.chat(
                    model=self._MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                            "images": [str(temporary_path)],
                        }
                    ],
                    format=schema,
                    options={"temperature": 0},
                )
            except ollama.ResponseError as exc:
                raise RuntimeError(
                    f"Ollama failed to analyze the image: {exc.error}"
                ) from exc
            except Exception as exc:
                raise RuntimeError(
                    "Unable to communicate with local Ollama. Ensure Ollama is "
                    "running and the gemma4:e2b model is installed."
                ) from exc

            content = response.message.content
            if not content:
                raise RuntimeError(
                    "Gemma returned an empty image analysis response."
                )

            try:
                return ImageAnalysisResult.model_validate_json(content)
            except ValidationError as exc:
                raise RuntimeError(
                    "Gemma returned invalid image analysis JSON; expected "
                    "issue_type and description as strings and confidence as "
                    "a number."
                ) from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError as exc:
                    raise RuntimeError(
                        "Failed to delete the temporary image after analysis."
                    ) from exc

    @staticmethod
    def _detect_image_suffix(image_bytes: bytes) -> str:
        """Return a safe file suffix for a supported image byte sequence."""
        if not image_bytes:
            raise ValueError("Image bytes must not be empty.")
        if image_bytes.startswith(b"\xff\xd8\xff"):
            return ".jpg"
        if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"

        raise ValueError("Unsupported image format; expected JPEG or PNG bytes.")
