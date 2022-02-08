import imp
from multiprocessing.spawn import import_main_path
import os
import secrets
from datetime import datetime
from urllib.parse import urlparse
import json
from time import sleep
import requests

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from link_dealer import schemas

router = APIRouter()
security = HTTPBasic()

username = os.environ.get('API_USERNAME', 'root')
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


@router.post('/make-utm')
def make_utm(utm_info: schemas.utm_info, _: str = Depends(get_current_username)) -> schemas.utms:
    category = urlparse(utm_info.link)[2].split('/')[-2].replace('-', '')
    term = f'{utm_info.item_type}-item-{category}'
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
        elif content_settings == 'to_main':
            url = main_url
        else:
            utm_content = f'utm_content={content_settings}'
        link = url + '?' + '&'.join([utm_source, utm_medium, utm_campaign, utm_content, term]),
        result.utms.append(
            schemas.utm(
                desc=content_settings,
                link=link,
                short_link=get_bitly(link)
            )
        )
    return result


def get_bitly(long_url):
    headers = {
        'Authorization': TOKEN_BITLY,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        'long_url': long_url,
        'domain': 'bit.ly',
        'group_guid': ''
    })
    url = 'https://api-ssl.bitly.com/v4/shorten'
    req = requests.post(url, headers=headers, data=payload)
    sleep(1)
    if req.status_code == 200:
        req_json = json.loads(req.text)
        return req_json['link']
    else:
        return 'bit.ly failed'
