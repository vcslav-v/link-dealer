from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column
from datetime import datetime


class Base(DeclarativeBase):
    pass


medium_source = Table(
    'medium_source',
    Base.metadata,
    Column('medium_id', ForeignKey('medium.id')),
    Column('source_id', ForeignKey('source.id')),
)


class Link(Base):
    '''Link.'''

    __tablename__ = 'link'

    id: Mapped[int] = mapped_column(primary_key=True)
    target_url: Mapped[str] = mapped_column()
    campaign_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    campaign_dop: Mapped[str] = mapped_column(default='0')
    full_url: Mapped[str] = mapped_column()

    term_material_id: Mapped[int] = mapped_column(ForeignKey('term_material.id'))
    term_material: Mapped['TermMaterial'] = relationship('TermMaterial', back_populates='links')

    term_page_id: Mapped[int] = mapped_column(ForeignKey('term_page.id'))
    term_page: Mapped['TermPage'] = relationship('TermPage', back_populates='links')

    medium_id: Mapped[int] = mapped_column(ForeignKey('medium.id'))
    medium: Mapped['Medium'] = relationship('Medium', back_populates='links')

    source_id: Mapped[int] = mapped_column(ForeignKey('source.id'))
    source: Mapped['Source'] = relationship('Source', back_populates='links')

    campaign_project_id: Mapped[int] = mapped_column(ForeignKey('campaign_project.id'))
    campaign_project: Mapped['CampaignProject'] = relationship('CampaignProject', back_populates='links')

    content_id: Mapped[int] = mapped_column(ForeignKey('content.id'))
    content: Mapped['Content'] = relationship('Content', back_populates='links')

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship('User', back_populates='links')


class TermMaterial(Base):
    '''TermMaterial.'''

    __tablename__ = 'term_material'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='term_material')


class TermPage(Base):
    '''TermPage.'''

    __tablename__ = 'term_page'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='term_page')


class Medium(Base):
    '''Medium.'''

    __tablename__ = 'medium'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='medium')

    sources: Mapped[list['Source']] = relationship(
        'Source',
        secondary=medium_source,
        back_populates='mediums',
    )


class Source(Base):
    '''Source.'''

    __tablename__ = 'source'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='source')

    mediums: Mapped[list['Medium']] = relationship(
        'Medium',
        secondary=medium_source,
        back_populates='sources',
    )


class CampaignProject(Base):
    '''CampaignProject.'''

    __tablename__ = 'campaign_project'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='campaign_project')


class Content(Base):
    '''Content.'''

    __tablename__ = 'content'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='content')


class User(Base):
    '''User.'''

    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    is_bot: Mapped[bool] = mapped_column(default=False)
    weight: Mapped[int] = mapped_column(default=0)

    links: Mapped[list['Link']] = relationship('Link', back_populates='user')
