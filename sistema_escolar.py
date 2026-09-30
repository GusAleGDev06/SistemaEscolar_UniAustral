from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Time, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum

# 1. Configuración de la base de datos
# Se creará un archivo llamado 'escuela.db' automáticamente en tu carpeta
engine = create_engine('sqlite:///escuela.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# 2. Definimos los días de la semana para evitar errores de escritura
class DiaSemana(enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    DOMINGO = "Domingo"

print("Configuración inicial lista. Base de datos conectada.")

# 3. Tabla de asociación Muchos a Muchos entre Curso y Profesor
curso_profesor = Table(
    'curso_profesor', Base.metadata,
    Column('curso_id', Integer, ForeignKey('cursos.id'), primary_key=True),
    Column('profesor_id', Integer, ForeignKey('profesores.id'), primary_key=True)
)

# 4. Definición de los Modelos (Tablas)
class Curso(Base):
    __tablename__ = 'cursos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    
    # Relaciones
    alumnos = relationship("Alumno", back_populates="curso")
    profesores = relationship("Profesor", secondary=curso_profesor, back_populates="cursos")
    horarios = relationship("Horario", back_populates="curso")

class Alumno(Base):
    __tablename__ = 'alumnos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    curso_id = Column(Integer, ForeignKey('cursos.id')) 
    
    curso = relationship("Curso", back_populates="alumnos")

class Profesor(Base):
    __tablename__ = 'profesores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    
    cursos = relationship("Curso", secondary=curso_profesor, back_populates="profesores")
    horarios = relationship("Horario", back_populates="profesor")

class Horario(Base):
    __tablename__ = 'horarios'
    id = Column(Integer, primary_key=True)
    dia = Column(Enum(DiaSemana), nullable=False)
    hora_desde = Column(Time, nullable=False)
    hora_hasta = Column(Time, nullable=False)
    
    curso_id = Column(Integer, ForeignKey('cursos.id'), nullable=False)
    profesor_id = Column(Integer, ForeignKey('profesores.id'), nullable=False)
    
    curso = relationship("Curso", back_populates="horarios")
    profesor = relationship("Profesor", back_populates="horarios")

# 5. Crear las tablas físicamente en la base de datos
Base.metadata.create_all(engine)
print("Tablas creadas exitosamente en la base de datos.")

from datetime import time

# ==========================================
# 6. FUNCIONES DE GESTIÓN (Registrar datos)
# ==========================================

def crear_curso(nombre):
    curso = Curso(nombre=nombre)
    session.add(curso)
    session.commit()
    print(f"✅ Curso '{nombre}' creado con ID {curso.id}.")
    return curso

def crear_alumno(nombre, curso_id):
    alumno = Alumno(nombre=nombre, curso_id=curso_id)
    session.add(alumno)
    session.commit()
    print(f"✅ Alumno '{nombre}' registrado en el curso ID {curso_id}.")

def crear_profesor(nombre):
    profesor = Profesor(nombre=nombre)
    session.add(profesor)
    session.commit()
    print(f"✅ Profesor '{nombre}' creado con ID {profesor.id}.")
    return profesor

def asignar_profesor_a_curso(profesor_id, curso_id):
    profesor = session.query(Profesor).get(profesor_id)
    curso = session.query(Curso).get(curso_id)
    if profesor and curso:
        curso.profesores.append(profesor)
        session.commit()
        print(f"✅ Profesor '{profesor.nombre}' asignado al curso '{curso.nombre}'.")
    else:
        print("❌ Error: Profesor o Curso no encontrado.")

def agregar_horario(curso_id, profesor_id, dia, hora_desde, hora_hasta):
    # hora_desde y hora_hasta deben ser objetos de tipo datetime.time (ej. time(8, 0))
    horario = Horario(
        curso_id=curso_id, 
        profesor_id=profesor_id, 
        dia=dia, 
        hora_desde=hora_desde, 
        hora_hasta=hora_hasta
    )
    session.add(horario)
    session.commit()
    print(f"✅ Horario agregado para el curso ID {curso_id} con el profesor ID {profesor_id}.")

# ==========================================
# 7. FUNCIONES DE EXPORTACIÓN (Reportes)
# ==========================================

def exportar_alumnos_de_curso(curso_id):
    curso = session.query(Curso).get(curso_id)
    if not curso:
        print("❌ Curso no encontrado.")
        return
    
    print(f"\n--- 📋 ALUMNOS DEL CURSO: {curso.nombre} ---")
    if not curso.alumnos:
        print("No hay alumnos registrados en este curso.")
    for alumno in curso.alumnos:
        print(f"- {alumno.nombre}")

def exportar_horario_profesor(profesor_id):
    profesor = session.query(Profesor).get(profesor_id)
    if not profesor:
        print("❌ Profesor no encontrado.")
        return
    
    print(f"\n--- 🕒 HORARIO DEL PROFESOR: {profesor.nombre} ---")
    if not profesor.horarios:
        print("El profesor no tiene horarios asignados.")
    for horario in profesor.horarios:
        print(f"- {horario.dia.value}: {horario.curso.nombre} de {horario.hora_desde} a {horario.hora_hasta}")

def exportar_horario_curso(curso_id):
    curso = session.query(Curso).get(curso_id)
    if not curso:
        print("❌ Curso no encontrado.")
        return
    
    print(f"\n--- 🕒 HORARIO DEL CURSO: {curso.nombre} ---")
    if not curso.horarios:
        print("El curso no tiene horarios asignados.")
    for horario in curso.horarios:
        print(f"- {horario.dia.value}: Prof. {horario.profesor.nombre} de {horario.hora_desde} a {horario.hora_hasta}")

# ==========================================
# 8. BLOQUE PRINCIPAL (Prueba del sistema)
# ==========================================

if __name__ == '__main__':
    print("🚀 Iniciando sistema escolar...\n")
    
    # 1. Crear Cursos
    print("--- Creando Cursos ---")
    curso_mate = crear_curso("Matemáticas")
    curso_hist = crear_curso("Historia")
    
    # 2. Crear Profesores
    print("\n--- Creando Profesores ---")
    prof_juan = crear_profesor("Juan Pérez")
    prof_maria = crear_profesor("María López")
    
    # 3. Asignar Profesores a Cursos (Relación Muchos a Muchos)
    print("\n--- Asignando Profesores ---")
    asignar_profesor_a_curso(prof_juan.id, curso_mate.id)
    asignar_profesor_a_curso(prof_maria.id, curso_mate.id)
    asignar_profesor_a_curso(prof_juan.id, curso_hist.id)
    
    # 4. Crear Alumnos y asignarlos a un curso (Relación Uno a Muchos)
    print("\n--- Registrando Alumnos ---")
    crear_alumno("Ana Gómez", curso_mate.id)
    crear_alumno("Carlos Ruiz", curso_mate.id)
    crear_alumno("Luis Torres", curso_hist.id)
    
    # 5. Agregar Horarios (Curso, Profesor, Día, Hora Inicio, Hora Fin)
    print("\n--- Agregando Horarios ---")
    agregar_horario(curso_mate.id, prof_juan.id, DiaSemana.LUNES, time(8, 0), time(10, 0))
    agregar_horario(curso_mate.id, prof_maria.id, DiaSemana.MARTES, time(10, 0), time(12, 0))
    agregar_horario(curso_hist.id, prof_juan.id, DiaSemana.MIERCOLES, time(14, 0), time(16, 0))
    
    # 6. Ejecutar Exportaciones (Reportes)
    print("\n" + "="*40)
    print("📊 REPORTES DEL SISTEMA")
    print("="*40)
    
    # Exportar alumnos de un curso
    exportar_alumnos_de_curso(curso_mate.id)
    
    # Exportar horario de un profesor
    exportar_horario_profesor(prof_juan.id)
    
    # Exportar horario de un curso
    exportar_horario_curso(curso_mate.id)
    
    print("\n✅ ¡Prueba finalizada con éxito!")        