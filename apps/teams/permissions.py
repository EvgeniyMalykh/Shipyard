class IsTeamMember(BasePermission):
    """Request user must be a member of the team in the URL kwargs."""

class IsTeamAdmin(BasePermission):
    """Request user must have role=admin or role=owner on the team."""

class IsTeamOwner(BasePermission):
    """Request user must have role=owner on the team."""
    # Used for: team deletion, owner transfer, billing management

class IsTeamOwnerOrAdmin(BasePermission):
    """Either owner or admin; used for most write operations."""