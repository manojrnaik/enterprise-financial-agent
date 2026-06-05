import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from src.database.vector_store import VectorStorageEngine

load_dotenv()

# Define a custom CrewAI execution tool bound directly to our Semantic Retriever
@tool("Query Financial Document Vector Store")
def query_vector_store(search_query: str) -> str:
    """Useful when you need to search and extract semantic text chunks from uploaded annual reports and financial statements."""
    db_engine = VectorStorageEngine()
    retriever = db_engine.get_retriever()
    matched_documents = retriever.invoke(search_query)
    
    # Format and present source page markers to the agent to enforce citation paths
    formatted_context = []
    for doc in matched_documents:
        page_num = doc.metadata.get("page", "Unknown")
        formatted_context.append(f"[Source Page: {page_num}]\nContent: {doc.page_content}")
        
    return "\n\n---\n\n".join(formatted_context)


class FinancialAnalysisCrew:
    def __init__(self):
        # Load local configuration manifests safely
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        
        with open(os.path.join(self.config_dir, "agents.yaml"), "r") as f:
            self.agents_config = yaml.safe_load(f)
            
        with open(os.path.join(self.config_dir, "tasks.yaml"), "r") as f:
            self.tasks_config = yaml.safe_load(f)
            
        # Initialize production-grade orchestration engine model
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

    def assemble_crew(self) -> Crew:
        # 1. Initialize Agents
        research_agent = Agent(
            config=self.agents_config['research_agent'],
            tools=[query_vector_store],
            llm=self.llm,
            verbose=True
        )
        
        analysis_agent = Agent(
            config=self.agents_config['analysis_agent'],
            tools=[],  # Relies solely on cognitive reasoning and mathematical verification
            llm=self.llm,
            verbose=True
        )
        
        # 2. Map Concrete Tasks
        extraction_task = Task(
            config=self.tasks_config['data_extraction_task'],
            agent=research_agent
        )
        
        evaluation_task = Task(
            config=self.tasks_config['financial_evaluation_task'],
            agent=analysis_agent
        )
        
        # 3. Compile Execution Topology
        return Crew(
            agents=[research_agent, analysis_agent],
            tasks=[extraction_task, evaluation_task],
            process=Process.sequential,
            verbose=True
        )

if __name__ == "__main__":
    print("🤖 Testing structural Multi-Agent compilation...")
    crew_instance = FinancialAnalysisCrew().assemble_crew()
    print("✅ Crew compiled successfully without dependency errors.")
