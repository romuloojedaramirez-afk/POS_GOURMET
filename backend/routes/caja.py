from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import SesionCaja, Pedido, EstadoPedido
from ..schemas import AbrirCaja, CerrarCaja, SesionCajaOut

router = APIRouter()


@router.get("/sesion-activa", response_model=SesionCajaOut)
def sesion_activa(db: Session = Depends(get_db)):
    sesion = db.query(SesionCaja).filter(SesionCaja.estado == "abierta").first()
    if not sesion:
        raise HTTPException(status_code=404, detail="No hay sesión de caja abierta")
    return sesion


@router.post("/abrir", response_model=SesionCajaOut)
def abrir_caja(data: AbrirCaja, db: Session = Depends(get_db)):
    abierta = db.query(SesionCaja).filter(SesionCaja.estado == "abierta").first()
    if abierta:
        raise HTTPException(status_code=400, detail="Ya hay una sesión de caja abierta")
    sesion = SesionCaja(
        monto_inicial=data.monto_inicial,
        abierta_por=data.abierta_por,
    )
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return sesion


@router.post("/cerrar")
def cerrar_caja(data: CerrarCaja, db: Session = Depends(get_db)):
    sesion = db.query(SesionCaja).filter(SesionCaja.estado == "abierta").first()
    if not sesion:
        raise HTTPException(status_code=404, detail="No hay sesión activa")

    sesion.monto_final = data.monto_final
    sesion.estado = "cerrada"
    sesion.cerrada_at = datetime.utcnow()
    db.commit()

    diferencia = data.monto_final - (sesion.monto_inicial + sesion.total_efectivo)
    return {
        "ok": True,
        "total_ventas": sesion.total_ventas,
        "total_efectivo": sesion.total_efectivo,
        "total_digital": sesion.total_digital,
        "diferencia_caja": round(diferencia, 2),
        "cerrada_at": sesion.cerrada_at.isoformat(),
    }


@router.get("/historial")
def historial_sesiones(db: Session = Depends(get_db)):
    sesiones = db.query(SesionCaja).order_by(SesionCaja.created_at.desc()).limit(30).all()
    return sesiones


@router.get("/resumen-hoy")
def resumen_hoy(db: Session = Depends(get_db)):
    hoy = datetime.utcnow().date()
    pedidos_hoy = db.query(Pedido).filter(
        Pedido.estado == EstadoPedido.entregado,
        Pedido.cerrado_at >= datetime.combine(hoy, datetime.min.time()),
    ).all()

    total = sum(p.total for p in pedidos_hoy)
    por_metodo = {}
    for p in pedidos_hoy:
        metodo = p.metodo_pago.value if p.metodo_pago else "sin_pago"
        por_metodo[metodo] = por_metodo.get(metodo, 0) + p.total

    return {
        "fecha": str(hoy),
        "total_pedidos": len(pedidos_hoy),
        "total_ventas": round(total, 2),
        "por_metodo_pago": {k: round(v, 2) for k, v in por_metodo.items()},
        "ticket_promedio": round(total / len(pedidos_hoy), 2) if pedidos_hoy else 0,
    }
