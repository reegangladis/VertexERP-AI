import math
from typing import Any


def get_pagination_metadata(total_count: int, skip: int, limit: int) -> dict[str, Any]:
    """Generates standard pagination metadata dictionary."""
    limit = max(1, limit)
    current_page = (skip // limit) + 1
    total_pages = math.ceil(total_count / limit)

    return {
        "total_count": total_count,
        "limit": limit,
        "skip": skip,
        "page": current_page,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_previous": current_page > 1,
    }
