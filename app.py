import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from models import db, User, Role, Permission, Medico, ObraSocial, Paciente, Turno
from forms import LoginForm, MedicoForm, ObraSocialForm, PacienteForm, TurnoForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from datetime import datetime, date
import io
import pandas as pd

# ----------------------- Configuración Flask -----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ----------------------- Inicializar DB y Login -----------------------
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------------- Adaptación User para Flask-Login -----------------------
class UserModel(UserMixin, User):
    pass

@login_manager.user_loader
def load_user(user_id):
    u = User.query.get(int(user_id))
    if not u:
        return None
    um = UserModel()
    um.__dict__.update(u.__dict__)
    um.id = u.id
    return um

# ----------------------- Inicializar Base de Datos -----------------------
def init_db():
    with app.app_context():
        db.create_all()

        # Crear permisos y roles base
        if Permission.query.count() == 0:
            perms = ['medicos', 'obras_sociales', 'pacientes', 'turnos', 'estadisticas', 'usuarios']
            for p in perms:
                db.session.add(Permission(name=p, description=f'Acceso a {p}'))
            db.session.commit()

        if Role.query.count() == 0:
            admin = Role(name='admin', description='Administrador')
            recepcion = Role(name='recepcion', description='Recepcion')
            admin.permissions = Permission.query.all()
            recepcion.permissions = Permission.query.filter(Permission.name.in_(['pacientes','turnos','obras_sociales'])).all()
            db.session.add_all([admin, recepcion])
            db.session.commit()

        if User.query.count() == 0:
            admin_user = User(username='admin', password_hash=generate_password_hash('adminpass'),
                              full_name='Administrador',
                              role=Role.query.filter_by(name='admin').first())
            db.session.add(admin_user)
            db.session.commit()


# ----------------------- Rutas Login -----------------------
@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u and check_password_hash(u.password_hash, form.password.data):
            user = load_user(u.id)
            login_user(user)
            flash('Bienvenido '+(u.full_name or u.username))
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ----------------------- Dashboard -----------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ----------------------- CRUD Médicos -----------------------
@app.route('/medicos', methods=['GET','POST'])
@login_required
def medicos():
    if not current_user.has_permission('medicos'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    form = MedicoForm()
    if form.validate_on_submit():
        m = Medico(nombre=form.nombre.data, apellido=form.apellido.data, especialidad=form.especialidad.data)
        db.session.add(m)
        db.session.commit()
        flash('Médico creado')
        return redirect(url_for('medicos'))

    medicos = Medico.query.all()
    return render_template('medicos.html', medicos=medicos, form=form)

# ----------------------- CRUD Obras Sociales -----------------------
@app.route('/obras', methods=['GET','POST'])
@login_required
def obras():
    if not current_user.has_permission('obras_sociales'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    form = ObraSocialForm()
    if form.validate_on_submit():
        o = ObraSocial(nombre=form.nombre.data)
        db.session.add(o)
        db.session.commit()
        flash('Obra Social creada')
        return redirect(url_for('obras'))

    obras = ObraSocial.query.all()
    return render_template('obras_sociales.html', obras=obras, form=form)

# ----------------------- CRUD Pacientes -----------------------
@app.route('/pacientes', methods=['GET','POST'])
@login_required
def pacientes():
    if not current_user.has_permission('pacientes'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    form = PacienteForm()
    form.obra_social.choices = [(0,'-- Ninguna --')] + [(o.id,o.nombre) for o in ObraSocial.query.all()]

    if form.validate_on_submit():
        obra_id = form.obra_social.data
        if obra_id == 0:
            obra_id = None
        p = Paciente(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            dni=form.dni.data,
            telefono=form.telefono.data,        # NUEVO
            direccion=form.direccion.data,      # NUEVO
            obra_social_id=obra_id
        )
        db.session.add(p)
        db.session.commit()
        flash('Paciente creado')
        return redirect(url_for('pacientes'))

    pacs = Paciente.query.all()
    return render_template('pacientes.html', pacientes=pacs, form=form)


# ----------------------- CRUD Turnos -----------------------
@app.route('/turnos', methods=['GET','POST'])
@login_required
def turnos():
    if not current_user.has_permission('turnos'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    form = TurnoForm()
    form.paciente.choices = [(p.id, f"{p.apellido}, {p.nombre}") for p in Paciente.query.all()]
    form.medico.choices = [(m.id, f"{m.apellido}, {m.nombre} ({m.especialidad})") for m in Medico.query.all()]
    form.obra_social.choices = [(0,'-- Ninguna --')] + [(o.id,o.nombre) for o in ObraSocial.query.all()]

    if form.validate_on_submit():
        obra_id = form.obra_social.data
        if obra_id == 0:
            obra_id = None
        t = Turno(
            fecha=form.fecha.data,
            paciente_id=form.paciente.data,
            medico_id=form.medico.data,
            especialidad=form.especialidad.data,
            precio=form.precio.data,
            usa_obra_social=form.usa_obra_social.data,
            obra_social_id=obra_id,
            pagado=form.pagado.data
        )
        db.session.add(t)
        db.session.commit()
        flash('Turno creado')
        return redirect(url_for('turnos'))

    turnos_list = Turno.query.order_by(Turno.fecha.desc()).all()
    return render_template('turnos.html', turnos=turnos_list, form=form)

# ----------------------- CRUD Usuarios -----------------------
from forms import UserForm  # Creamos este formulario para usuarios

@app.route('/usuarios', methods=['GET','POST'])
@login_required
def usuarios():
    if not current_user.has_permission('usuarios'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    form = UserForm()
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        # Crear nuevo usuario
        hashed = generate_password_hash(form.password.data)
        u = User(
            username=form.username.data,
            password_hash=hashed,
            full_name=form.full_name.data,
            role_id=form.role.data
        )
        db.session.add(u)
        db.session.commit()
        flash('Usuario creado correctamente')
        return redirect(url_for('usuarios'))

    users = User.query.all()
    roles = {r.id:r.name for r in Role.query.all()}
    return render_template('usuarios.html', users=users, roles=roles, form=form)


@app.route('/usuarios/editar/<int:user_id>', methods=['GET','POST'])
@login_required
def editar_usuario(user_id):
    if not current_user.has_permission('usuarios'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    u = User.query.get_or_404(user_id)
    form = UserForm(obj=u)
    form.role.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        u.username = form.username.data
        if form.password.data:
            u.password_hash = generate_password_hash(form.password.data)
        u.full_name = form.full_name.data
        u.role_id = form.role.data
        db.session.commit()
        flash('Usuario actualizado')
        return redirect(url_for('usuarios'))

    return render_template('editar_usuario.html', form=form, user=u)


@app.route('/usuarios/eliminar/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    if not current_user.has_permission('usuarios'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('Usuario eliminado')
    return redirect(url_for('usuarios'))


# ----------------------- Estadísticas -----------------------
@app.route('/estadisticas', methods=['GET'])
@login_required
def estadisticas():
    if not current_user.has_permission('estadisticas'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    hoy = date.today()
    turnos_hoy = Turno.query.filter(
        Turno.fecha >= datetime.combine(hoy, datetime.min.time()),
        Turno.fecha <= datetime.combine(hoy, datetime.max.time())
    ).order_by(Turno.fecha).all()

    total_recaudado = sum(t.precio for t in turnos_hoy if t.pagado)

    return render_template('estadisticas.html', turnos=turnos_hoy, total=total_recaudado)


# ----------------------- Exportar Excel -----------------------
@app.route('/estadisticas/export')
@login_required
def export_excel():
    if not current_user.has_permission('estadisticas'):
        flash('No tiene permiso', 'danger')
        return redirect(url_for('dashboard'))

    hoy = date.today()
    turnos_hoy = Turno.query.filter(
        Turno.fecha >= datetime.combine(hoy, datetime.min.time()),
        Turno.fecha <= datetime.combine(hoy, datetime.max.time())
    ).order_by(Turno.fecha).all()

    # Crear DataFrame
    data = []
    for t in turnos_hoy:
        data.append({
            "Fecha": t.fecha.strftime('%d/%m/%Y %H:%M'),
            "Paciente": f"{t.paciente.apellido}, {t.paciente.nombre}",
            "Médico": f"{t.medico.apellido}, {t.medico.nombre}",
            "Especialidad": t.especialidad,
            "Precio": t.precio,
            "Obra Social": t.obra_social.nombre if t.obra_social else "Ninguna",
            "Pagado": "Sí" if t.pagado else "No"
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Turnos del Día')

    output.seek(0)
    filename = f"Turnos_{hoy.strftime('%d-%m-%Y')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ----------------------- Inicialización y ejecución -----------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
