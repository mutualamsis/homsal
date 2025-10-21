from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.fields import DateTimeLocalField

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class MedicoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    especialidad = StringField('Especialidad', validators=[Optional()])
    submit = SubmitField('Guardar')

class ObraSocialForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class PacienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    dni = StringField('DNI', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[Optional()])
    direccion = StringField('Dirección', validators=[Optional()])
    obra_social = SelectField('Obra Social', coerce=int)

class TurnoForm(FlaskForm):
    fecha = DateTimeLocalField('Fecha y hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    paciente = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    medico = SelectField('Medico', coerce=int, validators=[DataRequired()])
    especialidad = StringField('Especialidad', validators=[Optional()])
    precio = DecimalField('Precio', places=2, validators=[DataRequired()])
    usa_obra_social = BooleanField('Usa obra social')
    obra_social = SelectField('Obra Social', coerce=int, validators=[Optional()])
    pagado = BooleanField('Pagado')
    submit = SubmitField('Guardar')

from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Contraseña', validators=[Optional()])  # obligatorio solo en creación
    full_name = StringField('Nombre completo', validators=[DataRequired()])
    role = SelectField('Rol', coerce=int, validators=[DataRequired()])

