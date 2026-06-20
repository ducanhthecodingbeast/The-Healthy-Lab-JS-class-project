from fastapi import HTTPException


DEFAULT_LIMIT = 100
MAX_LIMIT = 200
DEFAULT_OFFSET = 0


def validate_pagination(limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET) -> tuple[int, int]:
    if limit < 1 or limit > MAX_LIMIT:
        raise HTTPException(status_code=400, detail=f"limit must be between 1 and {MAX_LIMIT}")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be greater than or equal to 0")
    return limit, offset


def apply_pagination(query, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET):
    safe_limit, safe_offset = validate_pagination(limit, offset)
    return query.offset(safe_offset).limit(safe_limit)
