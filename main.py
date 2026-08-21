from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE LA BASE DE DATOS (SQLite)
# ==========================================
URL_BASE_DATOS = "sqlite:///./consultoria.db"

# connect_args={"check_same_thread": False} es necesario solo para SQLite
motor = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)
Base = declarative_base()

# ==========================================
# 2. MODELOS DE DATOS (Base de Datos vs Pydantic)
# ==========================================

# Modelo de la Base de Datos (SQLAlchemy - Cómo se guarda)
class ProspectoDB(Base):
    __tablename__ = "prospectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    correo = Column(String, index=True)
    institucion_o_empresa = Column(String)
    servicio_interes = Column(String)
    mensaje = Column(String)
    fecha_registro = Column(DateTime, default=datetime.now)

# Modelo de Validación (Pydantic - Cómo se recibe de la web)
class Contacto(BaseModel):
    nombre: str
    correo: EmailStr
    institucion_o_empresa: str
    servicio_interes: str
    mensaje: str

# Crear la base de datos y la tabla si no existen
Base.metadata.create_all(bind=motor)

# ==========================================
# 3. CONFIGURACIÓN DE FASTAPI
# ==========================================
app = FastAPI(title="API de Consultoría Estratégica")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para abrir y cerrar la conexión a la BD en cada petición
def obtener_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()

# ==========================================
# 4. RUTAS (ENDPOINTS)
# ==========================================

@app.post("/api/contacto", status_code=201)
async def procesar_contacto(formulario: Contacto, bd: Session = Depends(obtener_bd)):
    try:
        # Convertimos los datos validados de Pydantic al modelo de la Base de Datos
        nuevo_prospecto = ProspectoDB(
            nombre=formulario.nombre,
            correo=formulario.correo,
            institucion_o_empresa=formulario.institucion_o_empresa,
            servicio_interes=formulario.servicio_interes,
            mensaje=formulario.mensaje
        )
        
        # Guardamos en la base de datos
        bd.add(nuevo_prospecto)
        bd.commit()
        bd.refresh(nuevo_prospecto) # Para obtener el ID generado
        
        print(f"Éxito: Prospecto {nuevo_prospecto.nombre} guardado con el ID {nuevo_prospecto.id}")
        
        return {
            "mensaje": "¡Gracias por contactarnos! Tu solicitud ha sido registrada.",
            "id_registro": nuevo_prospecto.id
        }
        
    except Exception as e:
        bd.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar en la base de datos.")

@app.get("/")
async def root():
    return {"mensaje": "Servidor de Consultoría Activo y Conectado a BD"}