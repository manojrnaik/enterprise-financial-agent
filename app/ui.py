import streamlit as st
import requests

# Configure page layouts dynamically
st.set_page_config(
    page_title="Enterprise Financial Analyst AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Enterprise Financial Analyst AI")
st.caption("Production Multi-Agent RAG Pipeline for Advanced Corporate Document Auditing")

st.markdown("""
This system extracts structured balance sheet parameters via analytical semantic chunking pipelines, 
storing records inside an isolated local vector database instance before running a sequence of autonomous CrewAI validation tasks.
""")

# Create explicit structural layout containers
upload_col, display_col = st.columns([1, 2], gap="large")

with upload_col:
    st.subheader("Document Ingestion Hub")
    uploaded_file = st.file_uploader(
        "Upload Corporate Annual Financial PDF (10-K Report)", 
        type=["pdf"], 
        help="Upload files cleanly to trigger decoupled vector pipeline ingestion scripts."
    )
    
    trigger_analysis = st.button("🚀 Analyze Document Structure", use_container_width=True, disabled=not uploaded_file)

with display_col:
    st.subheader("Autonomous Auditor Output")
    
    if trigger_analysis and uploaded_file:
        with st.spinner("Processing document embeddings and executing internal Multi-Agent tasks..."):
            try:
                # Wrap file directly for standard HTTP multi-part transmission validation
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                # Make HTTP request directly to decoupled backend REST framework
                backend_url = "http://127.0.0"
                response = requests.post(backend_url, files=files, timeout=600)
                
                if response.status_code == 200:
                    api_data = response.json()
                    st.success("Analysis complete!")
                    # Render structured Markdown tables and output text smoothly
                    st.markdown(api_data["result"])
                else:
                    st.error(f"Backend Gateway Error (Status {response.status_code}): {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Connection Refused. Please verify your FastAPI backend server instance is up and listening on port 8000.")
            except Exception as e:
                st.error(f"Execution Error Encountered: {str(e)}")
    else:
        st.info("Upload an enterprise corporate PDF report on the left panel to execute multi-agent audit loops.")
