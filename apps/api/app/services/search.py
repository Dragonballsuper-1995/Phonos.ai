from typing import List
from app.models.phone import PhoneDetails
from app.db.queries import search_phones

async def perform_search(query: str) -> List[PhoneDetails]:
    # Placeholder for hybrid search (SQL + FTS + Vector)
    # Using the query from db layer
    return await search_phones(query)
