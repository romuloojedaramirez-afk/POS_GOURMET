from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import ConfigRestaurante
from ..schemas import ConfigUpdate, ConfigOut

router = APIRouter()


@router.get("/", response_model=List[ConfigOut])
def obtener_config(db: Session = Depends(get_db)):
    return db.query(ConfigRestaurante).all()


@router.get("/{clave}")
def obtener_valor(clave: str, db: Session = Depends(get_db)):
    conf = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == clave).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return {"clave": conf.clave, "valor": conf.valor}


@router.put("/{clave}")
def actualizar_config(clave: str, data: ConfigUpdate, db: Session = Depends(get_db)):
    conf = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == clave).first()
    if not conf:
        conf = ConfigRestaurante(clave=clave, valor=data.valor)
        db.add(conf)
    else:
        conf.valor = data.valor
    db.commit()
    return {"ok": True, "clave": clave, "valor": data.valor}


@router.post("/bulk")
def actualizar_bulk(datos: dict, db: Session = Depends(get_db)):
    for clave, valor in datos.items():
        conf = db.query(ConfigRestaurante).filter(ConfigRestaurante.clave == clave).first()
        if conf:
            conf.valor = str(valor)
        else:
            db.add(ConfigRestaurante(clave=clave, valor=str(valor)))
    db.commit()
    return {"ok": True, "actualizados": len(datos)}
