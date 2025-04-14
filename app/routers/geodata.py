from fastapi import APIRouter,  HTTPException
from sqlmodel import select, asc, func
from app.database import SessionDep
from app.models.geodata import Country, CountryPublic

router = APIRouter(
    prefix="/geodata",
    tags=["geodata"],
    dependencies=[],#[Depends(get_token_header)], # TODO add token auth
    responses={404: {"description": "Not found"}},
)

@router.get("/countries/", response_model=list[CountryPublic]) 
def read_countries(db: SessionDep):
    countries = db.exec(select(Country).order_by(asc(Country.iso2_code))).all()
    return countries

@router.get("/countries/{country_id}/", response_model=CountryPublic)
def read_country(country_id: int, db: SessionDep):
    country = db.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country


@router.get("/countries/iso/{iso_code}/", response_model=CountryPublic)
def read_country(iso_code: str, db: SessionDep):
    country = db.exec(select(Country)
                      .where(
                          (func.lower(Country.iso2_code) == iso_code.lower() )
                          | (func.lower(Country.iso3_code) == iso_code.lower())
                        )
                      ).first()
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country