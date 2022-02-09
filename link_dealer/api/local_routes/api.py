import json
import os
import secrets
from datetime import datetime
from urllib.parse import urlparse
from loguru import logger

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from link_dealer import schemas

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
@router.post('/make-utm')
def make_utm(utm_info: schemas.utm_info, _: str = Depends(get_current_username)) -> schemas.utms:
    logger.debug(utm_info)
    category = urlparse(utm_info.link)[2].split('/')[-2].replace('-', '')
    term = f'utm_term={utm_info.item_type}-item-{category}'
    dt = datetime.utcnow().date()
    result = schemas.utms()
    utm_source = f'utm_source={utm_cattegories[utm_info.source]["source"]}'
    utm_medium = f'utm_medium={utm_cattegories[utm_info.source]["medium"]}'
    utm_campaign = f'utm_campaign={utm_info.project}-{dt.strftime("%Y%m%d")}'

    for content_settings in utm_cattegories[utm_info.source]['content']:
        url = utm_info.link
        utm_content = 'utm_content=text'
        if content_settings == 'to_subscription':
            url = subscription_url
        elif content_settings == 'to_subscription_button':
            url = subscription_url
            utm_content = 'utm_content=button'
        elif content_settings == 'to_main':
            url = main_url
        else:
            utm_content = f'utm_content={content_settings}'
        link = url + '?' + '&'.join([utm_source, utm_medium, utm_campaign, utm_content, term])
        result.utms.append(
            schemas.utm(
                desc=content_settings,
                link=link,
                short_link=''
            )
        )
    return result
