import networkx as nx
import os

# We build a simple, hardcoded mock graph for the MVP.
# In production, this loads from Neo4j.

_graph = nx.DiGraph()

def _initialize_graph():
    global _graph
    
    # Define relationships: [Component] -> (causes) -> [Issue]
    _graph.add_edge("Snapdragon 8 Gen 1", "Overheating", weight=0.9)
    _graph.add_edge("Snapdragon 888", "Overheating", weight=0.85)
    _graph.add_edge("Exynos 2200", "Battery Drain", weight=0.8)
    _graph.add_edge("Exynos 990", "Thermal Throttling", weight=0.95)
    
    # Motherboard issues (fictionalized for demonstration, based on historical brand trends)
    _graph.add_edge("Poco X3 Pro", "Motherboard Dead", weight=0.99)
    _graph.add_edge("Asus ROG Phone 5", "Wifi IC Dead", weight=0.9)

def get_knowledge_graph():
    if len(_graph.nodes) == 0:
        _initialize_graph()
    return _graph

def filter_by_knowledge_graph(phone_candidates: list) -> list:
    """
    Takes a list of PhoneDetails objects.
    Checks the Knowledge Graph for known critical issues.
    Returns the filtered list of safe phones.
    """
    G = get_knowledge_graph()
    safe_phones = []
    
    for phone in phone_candidates:
        model = phone.model or ""
        specs = str(phone.raw_specs) if phone.raw_specs else ""
        full_name = f"{phone.brand} {phone.name} {phone.model} {phone.fullName}".lower()
        
        # Check model name for exact hardware defects
        has_critical_issue = False
        for node in G.nodes:
            n_lower = node.lower()
            if (n_lower in full_name or (model and model.lower() in n_lower)) and G.out_degree(node) > 0:
                for target in G.successors(node):
                    print(f"[KnowledgeGraph] BLOCKED: {full_name} has critical issue: {target}")
                    has_critical_issue = True
                    break
            
            # Check processor for thermal issues
            if specs and n_lower in specs.lower() and G.out_degree(node) > 0:
                for target in G.successors(node):
                    weight = G[node][target]['weight']
                    if weight > 0.8: # high severity
                        print(f"[KnowledgeGraph] BLOCKED: {full_name} uses {node} which causes {target}")
                        has_critical_issue = True
                        break
                        
            if has_critical_issue:
                break
                
        if not has_critical_issue:
            safe_phones.append(phone)
            
    return safe_phones
