from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseOption(BaseModel):
    '''BaseOption.'''

    ident: Optional[int] = None
    value: str


class Medium(BaseOption):
    '''Medium.'''

    sources: list['BaseOption'] = []


class User(BaseOption):
    '''User.'''
    is_bot: bool = False


class Link(BaseModel):
    '''Link.'''

    id: int
    target_url: str
    campaign_date: datetime
    campaign_dop: str
    full_url: str
    term_material_id: int
    term_material_name: str
    term_page_id: int
    term_page_name: str
    medium_id: int
    medium_name: str
    source_id: int
    source_name: str
    campaign_project_id: int
    campaign_project_name: str
    content_id: int
    content_name: str
    user_id: int
    user_name: str


class Info(BaseModel):
    '''Info.'''

    users: list['User'] = []
    term_materials: list['BaseOption'] = []
    term_pages: list['BaseOption'] = []
    mediums: list['Medium'] = []
    campaign_projects: list['BaseOption'] = []
    contents: list['BaseOption'] = []


class LinkCreate(BaseModel):
    '''LinkCreate.'''

    target_url: str
    source: int | str
    medium: int | str
    campaign_project: int | str
    campaning_dop: str = '0'
    content: int | str = '0'
    term_material: int | str
    term_page: int | str
    user: int | str


class LastLinks(BaseModel):
    '''LastLinks.'''

    links: list[Link] = []