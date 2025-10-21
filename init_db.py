from app import app, db
from models import User, Role, Permission
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Crear tablas
        db.create_all()

        # --- Permisos ---
        permisos = ['turnos', 'usuarios', 'medicos', 'pacientes', 'obras_sociales', 'estadisticas']
        for p_name in permisos:
            if not Permission.query.filter_by(name=p_name).first():
                db.session.add(Permission(name=p_name))
        db.session.commit()

        # --- Rol Admin ---
        rol_admin = Role.query.filter_by(name='admin').first()
        if not rol_admin:
            rol_admin = Role(name='admin', description='Administrador completo')
            db.session.add(rol_admin)
            db.session.commit()

        # Asignar todos los permisos al rol admin
        rol_admin.permissions = Permission.query.all()
        db.session.commit()

        # --- Usuario Admin ---
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),  # contraseña inicial
                full_name='Administrador',
                role=rol_admin
            )
            db.session.add(admin)
            db.session.commit()

        print("✅ Base de datos inicializada correctamente. Usuario admin creado: admin / admin123")

if __name__ == '__main__':
    init_db()
