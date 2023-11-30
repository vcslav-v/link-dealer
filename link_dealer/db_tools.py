from link_dealer import db, models, schemas
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode


def get_info() -> schemas.Info:
    '''Get info.'''

    with db.SessionLocal() as session:
        users = session.query(models.User).order_by(models.User.weight).all()
        term_materials = session.query(models.TermMaterial).order_by(models.TermMaterial.weight.desc()).all()
        term_pages = session.query(models.TermPage).order_by(models.TermPage.weight.desc()).all()
        mediums = session.query(models.Medium).order_by(models.Medium.weight.desc()).all()
        campaign_projects = session.query(models.CampaignProject).order_by(models.CampaignProject.weight.desc()).all()
        contents = session.query(models.Content).order_by(models.Content.weight.desc()).all()
        last_links = session.query(models.Link).order_by(models.Link.campaign_date.desc()).limit(10).all()

        return schemas.Info(
            users=[
                schemas.User(
                    ident=user.id,
                    value=user.name,
                    is_bot=user.is_bot,
                )
                for user in users
            ],
            term_materials=[
                schemas.BaseOption(
                    ident=term_material.id,
                    value=term_material.name,
                )
                for term_material in term_materials
            ],
            term_pages=[
                schemas.BaseOption(
                    ident=term_page.id,
                    value=term_page.name,
                )
                for term_page in term_pages
            ],
            mediums=[
                schemas.Medium(
                    ident=medium.id,
                    value=medium.name,
                    sources=[
                        schemas.BaseOption(
                            ident=source.id,
                            value=source.name,
                        )
                        for source in sorted(medium.sources, key=lambda x: x.weight, reverse=True)
                    ],
                )
                for medium in mediums
            ],
            campaign_projects=[
                schemas.BaseOption(
                    ident=campaign_project.id,
                    value=campaign_project.name,
                )
                for campaign_project in campaign_projects
            ],
            contents=[
                schemas.BaseOption(
                    ident=content.id,
                    value=content.name,
                )
                for content in contents
            ],
            last_links=[
                schemas.Link(
                    id=link.id,
                    target_url=link.target_url,
                    campaign_date=link.campaign_date,
                    campaign_dop=link.campaign_dop,
                    full_url=link.full_url,
                    term_material_id=link.term_material_id,
                    term_material_name=link.term_material.name,
                    term_page_id=link.term_page_id,
                    term_page_name=link.term_page.name,
                    medium_id=link.medium_id,
                    medium_name=link.medium.name,
                    source_id=link.source_id,
                    source_name=link.source.name,
                    campaign_project_id=link.campaign_project_id,
                    campaign_project_name=link.campaign_project.name,
                    content_id=link.content_id,
                    content_name=link.content.name,
                    user_id=link.user_id,
                    user_name=link.user.name,
                )
                for link in last_links
            ],

        )


def update_info(data: schemas.Info):
    '''Update info.'''
    with db.SessionLocal() as session:
        for user in data.users:
            if user.ident is None:
                session.query(models.User).filter(models.User.name == user.value).first() or session.add(models.User(name=user.value, is_bot=user.is_bot))
            else:
                session.query(models.User).filter(models.User.id == user.ident).update({'name': user.value})

        for term_material in data.term_materials:
            if term_material.ident is None:
                session.query(models.TermMaterial).filter(models.TermMaterial.name == term_material.value).first() or session.add(models.TermMaterial(name=term_material.value))
            else:
                session.query(models.TermMaterial).filter(models.TermMaterial.id == term_material.ident).update({'name': term_material.value})

        for term_page in data.term_pages:
            if term_page.ident is None:
                session.query(models.TermPage).filter(models.TermPage.name == term_page.value).first() or session.add(models.TermPage(name=term_page.value))
            else:
                session.query(models.TermPage).filter(models.TermPage.id == term_page.ident).update({'name': term_page.value})

        for medium in data.mediums:
            if medium.ident is None:
                db_medium = session.query(models.Medium).filter(models.Medium.name == medium.value).first()
                if not db_medium:
                    db_medium = models.Medium(name=medium.value)
                    session.add(db_medium)
                    session.commit()
            else:
                db_medium = session.query(models.Medium).filter(models.Medium.id == medium.ident).first()
                if not db_medium:
                    db_medium = models.Medium(name=medium.value)
                    session.add(db_medium)
                    session.commit()
                else:
                    db_medium.name = medium.value
                    session.commit()
            for source in medium.sources:
                if source.ident is None:
                    db_source = session.query(models.Source).filter_by(name=source.value).first()
                    if db_source and db_source in db_medium.sources:
                        continue
                    elif db_source:
                        db_medium.sources.append(db_source)
                    else:
                        db_source = models.Source(name=source.value)
                        db_medium.sources.append(db_source)
                else:
                    db_source = session.query(models.Source).filter_by(id=source.ident).first()
                    if db_source and db_source in db_medium.sources:
                        continue
                    elif db_source:
                        db_medium.sources.append(db_source)
                    else:
                        db_source = models.Source(name=source.value)
                        db_medium.sources.append(db_source)
            session.commit()

        for campaign_project in data.campaign_projects:
            if campaign_project.ident is None:
                session.query(models.CampaignProject).filter(models.CampaignProject.name == campaign_project.value).first() or session.add(models.CampaignProject(name=campaign_project.value))
            else:
                session.query(models.CampaignProject).filter(models.CampaignProject.id == campaign_project.ident).update({'name': campaign_project.value})

        for content in data.contents:
            if content.ident is None:
                session.query(models.Content).filter(models.Content.name == content.value).first() or session.add(models.Content(name=content.value))
            else:
                session.query(models.Content).filter(models.Content.id == content.ident).update({'name': content.value})

        session.commit()


def _make_utm_url(
    target_url: str,
    campaign_date: datetime,
    term_material: str,
    term_page: str,
    medium: str,
    source: str,
    campaign_project: str,
    content: str,
    campaning_dop: str | None = None,
) -> tuple[str, str]:
    '''Make utm url. Return tuple (target_url, utm_url).'''
    url_parts = urlparse(target_url)
    query = parse_qs(url_parts.query)
    query.update({
        'utm_source': [source],
        'utm_medium': [medium],
        'utm_campaign': [f'{campaign_project}-{campaign_date.strftime("%Y%m%d")}'],
        'utm_content': [content],
        'utm_term': [f'{term_material}-{term_page}-{campaning_dop or "0"}'],
    })
    utm_url_parts = url_parts._replace(query=urlencode(query, doseq=True))
    utm_url = utm_url_parts.geturl()
    
    return url_parts.geturl(), utm_url


def create_link(data: schemas.LinkCreate) -> schemas.Link:
    '''Create link.'''
    with db.SessionLocal() as session:
        campaign_date = datetime.now()
        if isinstance(data.term_material, int):
            db_term_material = session.query(models.TermMaterial).filter_by(id=data.term_material).first()
        elif isinstance(data.term_material, str):
            db_term_material = session.query(models.TermMaterial).filter_by(name=data.term_material).first()
        if not db_term_material:
            raise ValueError('TermMaterial not found')
        if isinstance(data.term_page, int):
            db_term_page = session.query(models.TermPage).filter_by(id=data.term_page).first()
        elif isinstance(data.term_page, str):
            db_term_page = session.query(models.TermPage).filter_by(name=data.term_page).first()
        if not db_term_page:
            raise ValueError('TermPage not found')
        if isinstance(data.medium, int):
            db_medium = session.query(models.Medium).filter_by(id=data.medium).first()
        elif isinstance(data.medium, str):
            db_medium = session.query(models.Medium).filter_by(name=data.medium).first()
        if not db_medium:
            raise ValueError('Medium not found')
        if isinstance(data.source, int):
            db_source = session.query(models.Source).filter_by(id=data.source).first()
        elif isinstance(data.source, str):
            db_source = session.query(models.Source).filter_by(name=data.source).first()
        if not db_source or db_source not in db_medium.sources:
            raise ValueError('Source not found')
        if isinstance(data.campaign_project, int):
            db_campaign_project = session.query(models.CampaignProject).filter_by(id=data.campaign_project).first()
        elif isinstance(data.campaign_project, str):
            db_campaign_project = session.query(models.CampaignProject).filter_by(name=data.campaign_project).first()
        if not db_campaign_project:
            raise ValueError('CampaignProject not found')
        if isinstance(data.content, int):
            db_content = session.query(models.Content).filter_by(id=data.content).first()
        elif isinstance(data.content, str):
            db_content = session.query(models.Content).filter_by(name=data.content).first()
        if not db_content:
            raise ValueError('Content not found')
        if isinstance(data.user, int):
            db_user = session.query(models.User).filter_by(id=data.user).first()
        elif isinstance(data.user, str):
            db_user = session.query(models.User).filter_by(name=data.user).first()
        if not db_user:
            raise ValueError('User not found')

        target_url, full_url = _make_utm_url(
            data.target_url,
            campaign_date,
            db_term_material.name,
            db_term_page.name,
            db_medium.name,
            db_source.name,
            db_campaign_project.name,
            db_content.name,
            data.campaning_dop
        )
        db_link = models.Link(
            target_url=target_url,
            full_url=full_url,
            campaign_date=campaign_date,
            term_material=db_term_material,
            term_page=db_term_page,
            medium=db_medium,
            source=db_source,
            campaign_project=db_campaign_project,
            content=db_content,
            user=db_user,
        )
        if data.campaning_dop:
            db_link.campaign_dop = data.campaning_dop

        session.add(db_link)
        session.commit()
        return schemas.Link(
            id=db_link.id,
            target_url=db_link.target_url,
            campaign_date=db_link.campaign_date,
            campaign_dop=db_link.campaign_dop,
            full_url=db_link.full_url,
            term_material_id=db_link.term_material_id,
            term_material_name=db_link.term_material.name,
            term_page_id=db_link.term_page_id,
            term_page_name=db_link.term_page.name,
            medium_id=db_link.medium_id,
            medium_name=db_link.medium.name,
            source_id=db_link.source_id,
            source_name=db_link.source.name,
            campaign_project_id=db_link.campaign_project_id,
            campaign_project_name=db_link.campaign_project.name,
            content_id=db_link.content_id,
            content_name=db_link.content.name,
            user_id=db_link.user_id,
            user_name=db_link.user.name,
        )
