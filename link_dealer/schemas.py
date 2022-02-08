from typing import Optional
from pydantic import BaseModel, validator
import json
import os


class utm_info(BaseModel):
    link: str
    source: str
    project: str
    item_type: str

    @validator('source')
    def check_source(cls, source):
        if source in json.loads(os.environ.get('UTM_CATS', '{}')):
            return source
        raise ValueError('Not valide site')

    @validator('item_type')
    def check_project(cls, item_type):
        if item_type not in ['premium', 'freebie', 'plus']:
            raise ValueError('Not valide item_type')
        return item_type


class utm(BaseModel):
    desc: str
    link: str
    short_link: str


class utms(BaseModel):
    utms: list[utm] = []
