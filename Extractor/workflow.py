# workflow.py
from langgraph.graph import StateGraph, END
from state import AgentState

# Import all modular nodes
from .nodes.link_lister import link_lister
from .nodes.url_list import url_list
from .nodes.classifier import classifier
from .nodes.image_crawler import image_crawler
from .nodes.audio_crawler import audio_crawler
from .nodes.web_crawler import web_crawler
from .nodes.cleaning_model import cleaning_model
from .nodes.skill_maker import skill_maker
from .nodes.duplicate_detector import duplicate_detector
from .nodes.skill_enhancement import skill_enhancement
from .nodes.datapool import datapool

def route_after_link_lister(state: AgentState) -> str:
    """Route based on whether the URL has already been visited."""
    if state.get("is_visited") == "Yes":
        return "end"
    return "url_list"

def route_by_type(state: AgentState) -> str:
    """Route to the appropriate crawler based on content type classification."""
    file_type = state.get("type")
    if file_type == "Image":
        return "image_crawler"
    elif file_type == "Audio":
        return "audio_crawler"
    else:
        return "web_crawler"

def route_by_duplicate(state: AgentState) -> str:
    """Route to skill enhancement if duplicate token match >= 75%, otherwise directly to datapool."""
    if state.get("duplicate") == "Yes":
        return "skill_enhancement"
    return "datapool"

def build_workflow():
    workflow = StateGraph(AgentState)
    
    # 1. Register all nodes in the graph
    workflow.add_node("link_lister", link_lister)
    workflow.add_node("url_list", url_list)
    workflow.add_node("classifier", classifier)
    workflow.add_node("image_crawler", image_crawler)
    workflow.add_node("audio_crawler", audio_crawler)
    workflow.add_node("web_crawler", web_crawler)
    workflow.add_node("cleaning_model", cleaning_model)
    workflow.add_node("skill_maker", skill_maker)
    workflow.add_node("duplicate_detector", duplicate_detector)
    workflow.add_node("skill_enhancement", skill_enhancement)
    workflow.add_node("datapool", datapool)
    
    # 2. Set the starting entry point
    workflow.set_entry_point("link_lister")
    
    # 3. Define conditional and linear edges
    workflow.add_conditional_edges(
        "link_lister",
        route_after_link_lister,
        {
            "url_list": "url_list",
            "end": END
        }
    )
    
    workflow.add_edge("url_list", "classifier")
    
    workflow.add_conditional_edges(
        "classifier",
        route_by_type,
        {
            "image_crawler": "image_crawler",
            "audio_crawler": "audio_crawler",
            "web_crawler": "web_crawler"
        }
    )
    
    # All crawlers funnel into the cleaning model node
    workflow.add_edge("image_crawler", "cleaning_model")
    workflow.add_edge("audio_crawler", "cleaning_model")
    workflow.add_edge("web_crawler", "cleaning_model")
    
    # Sequential extraction pipeline
    workflow.add_edge("cleaning_model", "skill_maker")
    workflow.add_edge("skill_maker", "duplicate_detector")
    
    # Duplicate checking branch (>= 75% token match vs brand new)
    workflow.add_conditional_edges(
        "duplicate_detector",
        route_by_duplicate,
        {
            "skill_enhancement": "skill_enhancement",
            "datapool": "datapool"
        }
    )
    
    workflow.add_edge("skill_enhancement", "datapool")
    workflow.add_edge("datapool", END)
    
    return workflow.compile()

# Compiled application ready to be invoked or served via FastAPI
app_workflow = build_workflow()