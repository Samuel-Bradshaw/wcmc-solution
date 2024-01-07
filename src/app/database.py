from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    backref
)

DATABASE_URL = "sqlite:///db.sqlite"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass

#
# Database schema
#

class SurveyLocationDB(Base):
    __tablename__ = "surveylocation"

    id: Mapped[int] = mapped_column(primary_key=True)
    locality: Mapped[str] = mapped_column(nullable=True, default=None)
    latitude: Mapped[float] = mapped_column(index=True)
    longitude: Mapped[float] = mapped_column(index=True)


class SpeciesDB(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    kingdom: Mapped[str]
    phylum: Mapped[str]
    species_class: Mapped[str]
    order: Mapped[str]
    family: Mapped[str]
    genus: Mapped[str]
    scientific_name_authorship: Mapped[str]


class SpeciesLocationDB(Base):
    __tablename__ = "specieslocations"

    id: Mapped[int] = mapped_column(primary_key=True)
    survey_location_id: Mapped[int] = mapped_column(
        ForeignKey("surveylocation.id", ondelete='CASCADE'),
        index=True
    )
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete='CASCADE'),
        index=True
    )
    survey_location = relationship(
        "SurveyLocationDB",
        backref=backref("species_locations", cascade="all")
    )
    species = relationship(
        "SpeciesDB",
        backref=backref("species_locations", cascade="all")
    )


Base.metadata.create_all(engine)

