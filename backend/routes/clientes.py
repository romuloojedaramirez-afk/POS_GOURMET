from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Cliente
from ..schemas import ClienteCreate, ClienteUpdate, ClienteOut

router = APIRouter()


@router.get("/", response_model=List[ClienteOut])
def listar_clientes(
    busqueda: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Cliente)
    if busqueda:
        q = q.filter(
            Cliente.nombre.ilike(f"%{busqueda}%") |
            Cliente.telefono.ilike(f"%{busqueda}%")
        )
    return q.order_by(Cliente.total_pedidos.desc()).limit(100).all()


@router.get("/buscar")
def buscar_por_telefono(telefono: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.telefono == telefono).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.get("/{cliente_id}/historial")
def historial_cliente(cliente_id: int, db: Session = Depends(get_db)):
    from ..models import Pedido, EstadoPedido
    pedidos = db.query(Pedido).filter(
        Pedido.cliente_id == cliente_id,
        Pedido.estado == EstadoPedido.entregado
    ).order_by(Pedido.created_at.desc()).limit(20).all()
    return [
        {
            "id": p.id,
            "ticket": p.numero_ticket,
            "total": p.total,
            "metodo_pago": p.metodo_pago.value if p.metodo_pago else None,
            "fecha": p.created_at.isoformat(),
            "items": len(p.detalles),
        }
        for p in pedidos
    ]


@router.post("/", response_model=ClienteOut)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    existe = db.query(Cliente).filter(Cliente.telefono == data.telefono).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese teléfono")
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cliente, k, v)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.post("/{cliente_id}/puntos")
def agregar_puntos(cliente_id: int, puntos: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.puntos_fidelidad += puntos
    db.commit()
    return {"ok": True, "puntos_total": cliente.puntos_fidelidad}
