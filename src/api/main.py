import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.ingestion.pipeline import IngestionPipeline
from src.database.vector_store import VectorStorageEngine
from src.agents.crew import FinancialAnalysisCrew

app = FastAPI(
    title="Enterprise Financial Analyst AI Core API", 
    version="1.0.0",
    description="Production-grade FastAPI Gateway serving multi-agent RAG pipelines."
)

# Enable CORS for standard decoupled frontend architectures
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary directory for handling document multi-part uploads securely
UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalysisResponse(BaseModel):
    status: str
    result: str

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    """
    Inbound Pipeline Trigger: Accepts PDF, processes semantic splits, 
    populates local vector store, and schedules Multi-Agent execution.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF uploads are accepted.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # 1. Stream file securely to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Trigger Ingestion and Processing Pipeline
        ingestion_engine = IngestionPipeline()
        semantic_chunks = ingestion_engine.process_pdf(file_path)

        # 3. Synchronize vector index to local storage database
        db_engine = VectorStorageEngine()
        db_engine.index_documents(semantic_chunks)

        # 4. Initialize and kick off CrewAI sequential agent loop
        print("🚀 Compiling agents and kicking off parallel analytical execution...")
        crew = FinancialAnalysisCrew().assemble_crew()
        crew_output = crew.kickoff()

        # Extract text result safely based on CrewAI version output definitions
        final_markdown_report = str(crew_output)

        return AnalysisResponse(
            status="Success",
            result=final_markdown_report
        )

    except Exception as e:
        print(f"❌ Production Engine Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Execution Error: {str(e)}")
        
    finally:
        # Cleanup temporary uploaded files to maintain local storage cleanliness
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    # Boot server locally on port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
