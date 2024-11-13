from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_secreto_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Página de inicio
@app.route('/')
def home():
    return render_template('login.html')

# Registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        # Verificar que el usuario no exista
        if User.query.filter_by(email=email).first():
            flash("Este correo ya está registrado")
            return redirect(url_for('register'))
        
        # Crear usuario
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registro exitoso")
        return redirect(url_for('login'))
    return render_template('register.html')

# Inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        # Validar credenciales
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Inicio de sesión exitoso")
            return redirect(url_for('dashboard'))
        flash("Correo o contraseña incorrectos")
    return render_template('login.html')

# Panel de usuario
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Solicitud de cita
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        
        # Crear nueva cita
        new_appointment = Appointment(user_id=session['user_id'], date=date, time=time)
        db.session.add(new_appointment)
        db.session.commit()
        flash("Cita programada con éxito")
        return redirect(url_for('dashboard'))
    return render_template('book_appointment.html')

# Cierre de sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Sesión cerrada")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
