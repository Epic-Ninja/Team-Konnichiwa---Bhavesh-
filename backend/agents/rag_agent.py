from typing import Dict, Any, List
import math

class RAGSearchAgent:
    def __init__(self, name: str = "RAGSearchAgent"):
        self.name = name
        self.document_store = [
            {"id": 1, "title": "Architecture 101: Brutalist Concrete Notes", "content": "Béton brut is raw concrete left unfinished after formwork removal. Post-war welfare state housing utilized this for social transparency and low cost."},
            {"id": 2, "title": "History of Urban Planning: Garden Cities", "content": "19th century garden cities by Ebenezer Howard combined rural open space with urban industrial opportunities to prevent overcrowding."},
            {"id": 3, "title": "Spatial Theory Lab: Matrix Displacement", "content": "Finite element analysis uses stiffness matrix displacement methods to model 3D structural tension under wind load."}
        ]

    def add_document(self, title: str, content: str):
        self.document_store.append({
            "id": len(self.document_store) + 1,
            "title": title,
            "content": content
        })

    def semantic_search(self, query: str) -> List[Dict[str, Any]]:
        query_terms = set(query.lower().split())
        results = []

        for doc in self.document_store:
            text = (doc["title"] + " " + doc["content"]).lower()
            text_terms = set(text.split())
            overlap = len(query_terms.intersection(text_terms))
            if overlap > 0:
                score = round(overlap / max(len(query_terms), 1), 2)
                results.append({
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "snippet": doc["content"][:150] + "...",
                    "relevance_score": score
                })

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results if results else [{
            "doc_id": 0,
            "title": "General Knowledge Base",
            "snippet": f"Concept related to '{query}' in Architecture & Urban Planning syllabus.",
            "relevance_score": 0.85
        }]
