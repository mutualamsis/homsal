from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ----------------------- Roles y Permisos -----------------------
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles')

# Tabla intermedia Role-Permission
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
)

# ----------------------- Usuarios -----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role')

    def has_permission(self, perm_name):
        if self.role:
            return any(p.name == perm_name for p in self.role.permissions)
        return False

# ----------------------- Médicos -----------------------
class Medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    especialidad = db.Column(db.String(50), nullable=False)

# ----------------------- Obras Sociales -----------------------
class ObraSocial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

# ----------------------- Pacientes -----------------------
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(100), nullable=True)
    obra_social_id = db.Column(db.Integer, db.ForeignKey('obra_social.id'))
    obra_social = db.relationship('ObraSocial')

# ----------------------- Turnos -----------------------
class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    paciente = db.relationship('Paciente')
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'))
    medico = db.relationship('Medico')
    especialidad = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    usa_obra_social = db.Column(db.Boolean, default=False)
    obra_social_id = db.Column(db.Integer, db.ForeignKey('obra_social.id'), nullable=True)
    obra_social = db.relationship('ObraSocial')
    pagado = db.Column(db.Boolean, default=False)
