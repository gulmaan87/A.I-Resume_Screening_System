"""
Database utility functions for common operations.
"""

from typing import Optional


def convert_mongo_doc(doc: Optional[dict]) -> Optional[dict]:
    """
    Convert MongoDB document to API-friendly format.
    
    Converts _id to id and removes _id field.
    
    Args:
        doc: MongoDB document (with _id) or None
    
    Returns:
        Document with id field (no _id) or None
    """
    if doc is None:
        return None
    
    # Create a copy to avoid mutating the original
    result = doc.copy()
    
    # Convert _id to id
    if "_id" in result:
        result["id"] = str(result["_id"])
        result.pop("_id", None)
    
    return result

