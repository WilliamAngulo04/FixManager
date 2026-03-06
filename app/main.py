from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from . import database
except ImportError:
    import database

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

current_user_id = None

# --- RUTAS DE ACCESO ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    global current_user_id
    user = db.query(database.User).filter(database.User.username == username, database.User.password == password).first()
    if user:
        current_user_id = user.id
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = None):
    return templates.TemplateResponse("register.html", {"request": request, "error": error})

@app.post("/register")
async def register(
    username: str = Form(...), password: str = Form(...), 
    nombre: str = Form(...), nombre_sucursal: str = Form(...),
    direccion: str = Form(...), db: Session = Depends(get_db)
):
    if db.query(database.User).filter(database.User.username == username).first():
        return RedirectResponse(url="/register?error=exists", status_code=303)
    try:
        nueva_suc = database.Sucursal(nombre_sucursal=nombre_sucursal, direccion=direccion)
        db.add(nueva_suc)
        db.flush()
        new_user = database.User(
            username=username, password=password, 
            nombre_completo=nombre, role="Administrador", 
            sucursal_id=nueva_suc.id
        )
        db.add(new_user)
        db.commit()
        return RedirectResponse(url="/login", status_code=303)
    except:
        db.rollback()
        return RedirectResponse(url="/register?error=db", status_code=303)

@app.get("/logout")
async def logout():
    global current_user_id
    current_user_id = None
    return RedirectResponse(url="/login", status_code=303)

# --- PANEL PRINCIPAL ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    if current_user_id is None:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(database.User).filter(database.User.id == current_user_id).first()
    tecnicos = []
    
    if user.role == "Administrador":
        orders = db.query(database.ServiceOrder).filter(database.ServiceOrder.sucursal_id == user.sucursal_id).all()
        tecnicos = db.query(database.User).filter(database.User.role == "Técnico", database.User.sucursal_id == user.sucursal_id).all()
    else:
        orders = db.query(database.ServiceOrder).filter(database.ServiceOrder.technician_id == user.id).all()
    
    metrics = {
        "totales": sum(o.total_price for o in orders) if orders else 0,
        "pendientes": len([o for o in orders if o.status == "Pendiente"]),
        "proceso": len([o for o in orders if o.status == "En reparación"]),
        "listos": len([o for o in orders if o.status == "Listo"])
    }
    
    return templates.TemplateResponse("index.html", {
        "request": request, "orders": orders, "user": user, "metrics": metrics, "tecnicos": tecnicos
    })

# --- GESTIÓN DE ÓRDENES ---

@app.post("/create-order/")
async def create_order(
    client_name: str = Form(...), 
    client_phone: str = Form(...), 
    device: str = Form(...), 
    description: str = Form(...), 
    total_price: float = Form(0.0),
    advance_payment: float = Form(0.0),
    technician_id: str = Form(None), 
    db: Session = Depends(get_db)
):
    user = db.query(database.User).filter(database.User.id == current_user_id).first()
    f_tech_id = None
    if user.role == "Técnico":
        f_tech_id = user.id
    elif technician_id and technician_id != "":
        f_tech_id = int(technician_id)
    
    new_order = database.ServiceOrder(
        client_name=client_name, client_phone=client_phone, device=device, 
        description=description, total_price=total_price, advance_payment=advance_payment, 
        sucursal_id=user.sucursal_id, technician_id=f_tech_id
    )
    db.add(new_order)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/update-status/{order_id}")
async def update_status(order_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    order = db.query(database.ServiceOrder).filter(database.ServiceOrder.id == order_id).first()
    if order:
        if order.status == "Entregado":
            return RedirectResponse(url="/?error=locked", status_code=303)
        if status == "Entregado":
            order.advance_payment = order.total_price
        order.status = status
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/edit-order-prices/{order_id}")
async def edit_order_prices(
    order_id: int, total_price: float = Form(...), 
    advance_payment: float = Form(...), db: Session = Depends(get_db)
):
    order = db.query(database.ServiceOrder).filter(database.ServiceOrder.id == order_id).first()
    if order and order.status != "Entregado":
        order.total_price = total_price
        order.advance_payment = advance_payment
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- OTRAS RUTAS ---

@app.get("/tecnicos", response_class=HTMLResponse)
async def technicians_page(request: Request, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == current_user_id).first()
    tecnicos = db.query(database.User).filter(database.User.role == "Técnico", database.User.sucursal_id == user.sucursal_id).all()
    return templates.TemplateResponse("tecnicos.html", {"request": request, "user": user, "tecnicos": tecnicos})

@app.post("/create-technician")
async def create_technician(
    username: str = Form(...), 
    password: str = Form(...), 
    nombre: str = Form(...), 
    db: Session = Depends(get_db)
):
    admin = db.query(database.User).filter(database.User.id == current_user_id).first()
    
    # 1. VALIDACIÓN: Verificar si el nombre de usuario ya existe
    existe = db.query(database.User).filter(database.User.username == username).first()
    if existe:
        # Si ya existe, redirigimos con un mensaje de error (puedes capturarlo en el HTML)
        return RedirectResponse(url="/tecnicos?error=user_exists", status_code=303)

    try:
        # 2. Si no existe, procedemos a crear el técnico
        new_tech = database.User(
            username=username, 
            password=password, 
            nombre_completo=nombre, 
            role="Técnico", 
            sucursal_id=admin.sucursal_id
        )
        db.add(new_tech)
        db.commit()
        return RedirectResponse(url="/tecnicos", status_code=303)
    except Exception as e:
        db.rollback() # Siempre haz rollback si algo sale mal
        return RedirectResponse(url="/tecnicos?error=db_error", status_code=303)

@app.get("/perfil", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == current_user_id).first()
    return templates.TemplateResponse("perfil.html", {"request": request, "user": user})
