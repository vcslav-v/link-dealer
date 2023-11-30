import json
import os
import secrets
from datetime import datetime
from urllib.parse import urlparse
from loguru import logger

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from link_dealer import schemas, db_tools


router = APIRouter()
security = HTTPBasic()

username = os.environ.get('API_USERNAME', 'api')
password = os.environ.get('API_PASSWORD', 'pass')
subscription_url = os.environ.get('SUB_URL', 'subscription_url')
main_url = os.environ.get('MAIN_URL', 'main_url')
utm_cattegories = json.loads(os.environ.get('UTM_CATS', '{}'))
TOKEN_BITLY = os.environ.get('TOKEN_BITLY', '')


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username


@logger.catch
@router.get('/info', response_model=schemas.Info, tags=['api'])
def info(_: str = Depends(get_current_username)) -> schemas.Info:
    return db_tools.get_info()


@logger.catch
@router.post('/update_info', response_model=schemas.Info, tags=['api'])
def update_info(data: schemas.Info, _: str = Depends(get_current_username)) -> schemas.Info:
    db_tools.update_info(data)
    return db_tools.get_info()


@logger.catch
@router.post('/create_link', response_model=schemas.Link, tags=['api'])
def create_link(data: schemas.LinkCreate, _: str = Depends(get_current_username)) -> schemas.Link:
    link = db_tools.create_link(data)
    return link
