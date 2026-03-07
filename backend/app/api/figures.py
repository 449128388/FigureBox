from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.figure import Figure
from app.schemas.figure import Figure as FigureSchema, FigureCreate, FigureUpdate
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=list[FigureSchema])
def get_figures(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    figures = db.query(Figure).offset(skip).limit(limit).all()
    return figures

@router.get("/{figure_id}", response_model=FigureSchema)
def get_figure(figure_id: int, db: Session = Depends(get_db)):
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    return figure

@router.post("/", response_model=FigureSchema)
def create_figure(figure: FigureCreate, db: Session = Depends(get_db)):
    db_figure = Figure(**figure.model_dump())
    db.add(db_figure)
    db.commit()
    db.refresh(db_figure)
    return db_figure

@router.put("/{figure_id}", response_model=FigureSchema)
def update_figure(figure_id: int, figure: FigureUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    db_figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    for key, value in figure.model_dump(exclude_unset=True).items():
        setattr(db_figure, key, value)
    db.commit()
    db.refresh(db_figure)
    return db_figure

@router.delete("/{figure_id}")
def delete_figure(figure_id: int, db: Session = Depends(get_db)):
    db_figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not db_figure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Figure not found"
        )
    db.delete(db_figure)
    db.commit()
    return {"message": "Figure deleted successfully"}
