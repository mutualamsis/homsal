from app import app, db
from models import Paciente, ObraSocial

def recreate_paciente():
    with app.app_context():
        # ⚠️ Borra la tabla paciente
        print("⚠️ Eliminando tabla paciente si existe...")
        db.session.execute('DROP TABLE IF EXISTS paciente')
        db.session.commit()

        # ⚡ Crea la tabla de nuevo con los nuevos campos
        print("Creando tabla paciente con telefono y direccion...")
        db.create_all()

        print("✅ Tabla paciente recreada correctamente.")

if __name__ == '__main__':
    recreate_paciente()
