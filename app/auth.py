from fastapi import Request, HTTPException
from . import database

# Función simple para verificar si el usuario es Admin
def admin_required(user: database.User):
    if not user or user.role != "Administrador":
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requiere rol de Administrador")
    return True