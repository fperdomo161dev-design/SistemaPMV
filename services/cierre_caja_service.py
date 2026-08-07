from datetime import datetime


def generar_cierre(db, usuario):

    # Obtener último cierre
    ultimo_cierre = db["cierres_caja"].find_one(
        sort=[("numero_cierre", -1)]
    )

    if ultimo_cierre:
        ultimo_numero = int(
            ultimo_cierre["numero_cierre"].replace("CIE-", "")
        )
        siguiente = ultimo_numero + 1
    else:
        siguiente = 1

    numero_cierre = f"CIE-{siguiente:06d}"

    # Facturas emitidas
    facturas_emitidas = list(
        db["facturas"].find(
            {"estado": "EMITIDA"}
        )
    )

    cantidad_facturas = len(facturas_emitidas)

    total_ventas = sum(
        float(f.get("total", 0))
        for f in facturas_emitidas
    )

    # Facturas anuladas
    facturas_anuladas = list(
        db["facturas"].find(
            {"estado": "ANULADA"}
        )
    )

    total_anulaciones = sum(
        float(f.get("total", 0))
        for f in facturas_anuladas
    )

    total_neto = total_ventas - total_anulaciones

    cierre_doc = {
        "numero_cierre": numero_cierre,
        "fecha_cierre": datetime.now(),
        "usuario": usuario,
        "cantidad_facturas": cantidad_facturas,
        "total_ventas": total_ventas,
        "total_anulaciones": total_anulaciones,
        "total_neto": total_neto,
    }

    db["cierres_caja"].insert_one(cierre_doc)

    return cierre_doc