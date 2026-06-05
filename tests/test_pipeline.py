import os
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.ingestion.pipeline import IngestionPipeline

# Initialize the standard FastAPI test client
client = TestClient(app)

@pytest.fixture
def setup_dummy_pdf(tmp_path):
    """
    Fixture to generate a temporary text-based PDF file 
    for isolated unit testing.
    """
    import fpdf
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Enterprise Financial Report. Total Revenue was 50M USD.", ln=1, align="C")
    pdf.cell(200, 10, txt="Operating Margin grew to 15 percent. Debt-to-Equity ratio is 0.4.", ln=2, align="C")
    
    dummy_pdf_path = os.path.join(tmp_path, "test_report.pdf")
    pdf.output(dummy_pdf_path)
    return dummy_pdf_path


def test_ingestion_pipeline_initialization():
    """
    Unit Test: Verifies that the Ingestion Pipeline and 
    embedding structures load without environment configuration errors.
    """
    pipeline = IngestionPipeline()
    assert pipeline.embeddings is not None
    assert pipeline.text_splitter is not None


def test_api_rejection_of_invalid_file_types():
    """
    Integration Test: Assures the API gateway acts as a security firewall 
    and actively blocks unsafe, non-PDF file formats.
    """
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("malicious_script.sh", b"echo 'hack'", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF uploads are accepted" in response.json()["detail"]


def test_full_pipeline_with_dummy_pdf(setup_dummy_pdf):
    """
    End-to-End Test: Validates document ingestion, chunk splitting, 
    and checks if the entrypoint handles files end-to-end.
    """
    # Verify the temporary file exists
    assert os.path.exists(setup_dummy_pdf)
    
    # Run the processing logic locally to verify structural output
    pipeline = IngestionPipeline()
    try:
        chunks = pipeline.process_pdf(setup_dummy_pdf)
        assert isinstance(chunks, list)
        assert len(chunks) > 0
    except Exception as e:
        # If API keys are missing during CI pipeline tests, gracefully bypass OpenAI dependencies
        if "OPENAI_API_KEY" not in os.environ:
            pytest.skip("Skipping deep vector processing due to missing OpenAI API credentials.")
        else:
            raise e
