from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./fix_manager.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Sucursal(Base):
    __tablename__ = "sucursales"
    id = Column(Integer, primary_key=True, index=True)
    nombre_sucursal = Column(String(100), unique=True, nullable=False)
    direccion = Column(String(200), nullable=True) # Nuevo campo
    
    usuarios = relationship("User", back_populates="sucursal")
    ordenes = relationship("ServiceOrder", back_populates="sucursal")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    nombre_completo = Column(String(150))
    
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)
    sucursal = relationship("Sucursal", back_populates="usuarios", lazy='joined')
    ordenes_asignadas = relationship("ServiceOrder", back_populates="tecnico")

class ServiceOrder(Base):
    __tablename__ = "service_orders"
    id = Column(Integer, primary_key=True, index=True)
    device = Column(String(100))
    description = Column(Text)
    status = Column(String(20), default="Pendiente")
    client_name = Column(String(100))
    client_phone = Column(String(20))
    total_price = Column(Float, default=0.0)
    advance_payment = Column(Float, default=0.0)
    
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    
    tecnico = relationship("User", back_populates="ordenes_asignadas")
    sucursal = relationship("Sucursal", back_populates="ordenes")

Base.metadata.create_all(bind=engine)