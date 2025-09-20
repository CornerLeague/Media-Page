"""
Sports-related schemas
"""

from .common import BaseSchema, IDMixin, TimestampMixin


class Sport(BaseSchema, IDMixin, TimestampMixin):
    """Sport schema placeholder"""
    name: str
    slug: str


class League(BaseSchema, IDMixin, TimestampMixin):
    """League schema placeholder"""
    name: str
    slug: str


class Team(BaseSchema, IDMixin, TimestampMixin):
    """Team schema placeholder"""
    name: str
    slug: str


class SportResponse(BaseSchema):
    """Sport response placeholder"""
    pass


class LeagueResponse(BaseSchema):
    """League response placeholder"""
    pass


class TeamResponse(BaseSchema):
    """Team response placeholder"""
    pass