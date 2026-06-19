from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Mesa, Pedido, EstadoMesa, EstadoPedido
from ..schemas import MesaCreate, MesaUpdate, MesaOut, PedidoOut

router = APIRouter()


@router.get("/", response_model=List[dict])
def listar_mesas(db: Session = Depends(get_db)):
    mesas = db.query(Mesa).filter(Mesa.activo == True).order_by(Mesa.numero).all()
    resultado = []
    for mesa in mesas:
        pedido_activo = db.query(Pedido).filter(
            Pedido.mesa_id == mesa.id,
            Pedido.estado.in_([EstadoPedido.pendiente, EstadoPedido.en_preparacion, EstadoPedido.listo])
        ).order_by(Pedido.created_at.desc()).first()

        resultado.append({
            "id": mesa.id,
            "numero": mesa.numero,
            "capacidad": mesa.capacidad,
            "estado": mesa.estado.value,
            "ubicacion": mesa.ubicacion,
            "pedido_activo_id": pedido_activo.id if pedido_activo else None,
            "total_pedido": pedido_activo.total if pedido_activo else 0,
            "items_count": len(pedido_activo.detalles) if pedido_activo else 0,
        })
    return resultado


@router.get("/{mesa_id}")
def obtener_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    return mesa


@router.post("/", response_model=dict)
def crear_mesa(data: MesaCreate, db: Session = Depends(get_db)):
    existe = db.query(Mesa).filter(Mesa.numero == data.numero).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe una mesa con ese número")
    mesa = Mesa(**data.model_dump())
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return {"id": mesa.id, "numero": mesa.numero, "estado": mesa.estado.value}


@router.put("/{mesa_id}/estado")
def actualizar_estado_mesa(mesa_id: int, data: MesaUpdate, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    if data.estado:
        mesa.estado = data.estado
    if data.capacidad:
        mesa.capacidad = data.capacidad
    if data.ubicacion:
        mesa.ubicacion = data.ubicacion
    db.commit()
    return {"ok": True, "estado": mesa.estado.value}


@router.delete("/{mesa_id}")
def eliminar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    mesa.activo = False
    db.commit()
    return {"ok": True}


@router.post("/configurar")
def configurar_mesas(cantidad: int, db: Session = Depends(get_db)):
    """Ajusta la cantidad total de mesas del restaurante."""
    if cantidad < 1 or cantidad > 100:
        raise HTTPException(status_code=400, detail="Cantidad debe ser entre 1 y 100")

    actuales = db.query(Mesa).filter(Mesa.activo == True).count()

    if cantidad > actuales:
        for i in range(actuales + 1, cantidad + 1):
            db.add(Mesa(numero=i, capacidad=4))
    elif cantidad < actuales:
        mesas_extra = db.query(Mesa).filter(
            Mesa.numero > cantidad, Mesa.activo == True
        ).all()
        for m in mesas_extra:
            m.activo = False

    db.commit()
    return {"ok": True, "mesas_activas": cantidad}
