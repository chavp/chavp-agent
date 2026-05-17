from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List, Annotated, Tuple
import os

from models import ResearchState
from agents.assistant_selector import select_assistant
from agents.web_researcher import generate_search_queries, perform_web_searches, summarize_search_results, evaluate_search_relevance
from agents.report_writer import write_research_report

from fastapi import FastAPI, Query

def create_research_graph() -> StateGraph:
    """
    Create the LangGraph research graph that coordinates the agents.
    """
    # Define the graph
    graph = StateGraph(ResearchState)
    
    # Add nodes to the graph
    graph.add_node("select_assistant", select_assistant)
    graph.add_node("generate_search_queries", generate_search_queries)
    graph.add_node("perform_web_searches", perform_web_searches)
    graph.add_node("summarize_search_results", summarize_search_results)
    graph.add_node("evaluate_search_relevance", evaluate_search_relevance)
    graph.add_node("write_research_report", write_research_report)
    
    # Define the conditional routing function for relevance evaluation
    def route_based_on_relevance(state: Dict[str, Any]) -> str:
        """
        Route to either generate new search queries or continue to report writing
        based on the relevance evaluation.
        """
        # Get the current iteration count
        iteration_count = state.get("iteration_count", 0)
        
        # Increment the iteration count
        new_iteration_count = iteration_count + 1
        
        # Update the state with the new iteration count
        state["iteration_count"] = new_iteration_count
        
        # Check if we've reached the maximum number of iterations (3)
        if new_iteration_count >= 3:
            print(f"Reached maximum iterations ({new_iteration_count}). Proceeding to write report with current results.")
            return "write_research_report"
        
        # Otherwise, check if we should regenerate queries
        if state.get("should_regenerate_queries", False):
            print(f"Iteration {new_iteration_count}: Regenerating search queries.")
            return "generate_search_queries"
        else:
            print(f"Iteration {new_iteration_count}: Search results are relevant. Proceeding to write report.")
            return "write_research_report"
    
    # Define the flow of the graph
    graph.add_edge("select_assistant", "generate_search_queries")
    graph.add_edge("generate_search_queries", "perform_web_searches")
    graph.add_edge("perform_web_searches", "summarize_search_results")
    graph.add_edge("summarize_search_results", "evaluate_search_relevance")
    
    # Add conditional routing based on relevance evaluation
    graph.add_conditional_edges(
        "evaluate_search_relevance",
        route_based_on_relevance,
        {
            "generate_search_queries": "generate_search_queries",
            "write_research_report": "write_research_report"
        }
    )
    
    graph.add_edge("write_research_report", END)
    
    # Set the entry point
    graph.set_entry_point("select_assistant")
    
    return graph

def run_research(question: str) -> str:
    """
    Run the research graph with a user question.
    
    Args:
        question: The user's research question
        
    Returns:
        The final research report
    """
    # Create the graph
    research_graph = create_research_graph()
    
    # Compile the graph
    app = research_graph.compile()
    
    # Initialize the state
    initial_state = {
        "user_question": question,
        "assistant_info": None,
        "search_queries": None,
        "search_results": None,
        "search_summaries": None,
        "research_summary": None,
        "final_report": None,
        "used_fallback_search": False,
        "relevance_evaluation": None,
        "should_regenerate_queries": None,
        "iteration_count": 0
    }
    
    # Run the graph
    result = app.invoke(initial_state)
    
    # Extract and return the final report
    return result["final_report"]

app = FastAPI(
    title="สร้างงานวิจัยด้วย LangGraph และ ChatGPT",
    description="API ค้นคว้างานวิจัย",
    version="1.0.0",
    terms_of_service="https://chavp.wordpress.com/about/",
    contact={
        "name": "ทีมพัฒนาซอฟต์แวร์",
        "url": "https://chavp.wordpress.com",
        "email": "my.parinya@gmail.com",
    },
)

@app.get("/run-info-cuda", tags=["system"], summary="แสดงข้อมูล run GPU")
def get_run_info_cuda():
    import torch
    # 1. ตรวจสอบว่าระบบรองรับ CUDA หรือไม่ (True/False)
    cuda_available = torch.cuda.is_available()

    if cuda_available:
        # 2. นับจำนวน GPU ที่มีในเครื่อง
        device_count = torch.cuda.device_count()

        # 3. ดูชื่อรุ่นของ GPU ตัวหลัก (ID: 0)
        current_device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_device)

        # 4. ดูสเปก Compute Capability ของ GPU
        capability = torch.cuda.get_device_capability(current_device)

        return {
            "cuda_available": cuda_available,
            "device_count": f"GPU Count: {device_count}",
            "current_device": f"Current GPU Device: ID {current_device} -> {gpu_name}",
            "capability": f"CUDA Capability: {capability[0]}.{capability[1]}"
        }
    else:
        return {
            "cuda_available": cuda_available,
            "torch.cuda.is_available": "PyTorch detect เฉพาะ CPU (ไม่พบ CUDA GPU หรือยังไม่ได้ติดตั้ง PyTorch เวอร์ชัน CUDA"
        }

@app.get("/researchs", tags=["research_agents"], summary="ใส่คำถามเพื่อวิจัย", description="What can I see and do in the Spanish town of Astorga?")
def get_chain_try_5_1(question: str = Query(..., description="test chain invocation")):
    report = run_research(question)
    return report