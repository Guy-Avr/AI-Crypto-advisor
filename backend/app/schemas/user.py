from pydantic import BaseModel


class UserMeResponse(BaseModel):
    """Current user info for GET /users/me (id, email, name, onboarding done)."""

    id: str
    email: str
    name: str
    onboarding_done: bool
