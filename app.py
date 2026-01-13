from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import io
# Imports de Ingeniería (PDF y QR)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import qrcode

app = Flask(__name__)
app.secret_key = 'clave_secreta_fase2'

# --- 1. CONFIGURACIÓN DB ---
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///mantenimiento_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. MODELOS RELACIONALES ---

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False) 
    direccion = db.Column(db.String(200))              
    # Relación mágica
    equipos = db.relationship('Equipo', backref='cliente', lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "direccion": self.direccion
        }

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    serial = db.Column(db.String(50), unique=True)
    ubicacion = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default='Operativo')
    observaciones = db.Column(db.String(200))
    # Foreign Key (La conexión)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "serial": self.serial,
            "ubicacion": self.ubicacion,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "cliente_id": self.cliente_id,
            "nombre_cliente": self.cliente.nombre if self.cliente else "Sin Cliente"
        }

with app.app_context():
    db.create_all()

# --- 3. RUTAS (VISTAS) ---

@app.route('/')
def dashboard():
    # 1. ¿Me están pidiendo un cliente específico? (ej: /?cliente_id=2)
    cliente_id_filtrado = request.args.get('cliente_id')
    
    # 2. Obtenemos la lista de TODOS los clientes (para llenar el selector)
    todos_los_clientes = Cliente.query.all()
    
    # 3. Decidimos qué equipos mostrar
    cliente_actual = None
    
    if cliente_id_filtrado:
        # Lógica de Filtrado: "SELECT * FROM equipo WHERE cliente_id = X"
        equipos_mostrar = Equipo.query.filter_by(cliente_id=cliente_id_filtrado).all()
        # Buscamos el nombre del cliente para ponerlo en el título
        cliente_actual = Cliente.query.get(cliente_id_filtrado)
    else:
        # Si no hay filtro, mostramos todo (Modo Dios)
        equipos_mostrar = Equipo.query.all()

    return render_template('index.html', 
                           equipos=equipos_mostrar, 
                           clientes=todos_los_clientes,
                           cliente_actual=cliente_actual)
# --- 4. API (CEREBRO) ---

# A. Para llenar la lista desplegable de Clientes
@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    clientes = Cliente.query.all()
    return jsonify([c.to_json() for c in clientes])

# B. Crear Equipo (Ahora recibe cliente_id)
@app.route('/api/equipos', methods=['POST'])
def agregar_equipo():
    datos = request.json
    try:
        nuevo = Equipo(
            nombre=datos['nombre'],
            tipo=datos['tipo'],
            serial=datos['serial'],
            ubicacion=datos['ubicacion'],
            observaciones=datos.get('observaciones', ''),
            cliente_id=int(datos['cliente_id']) # <--- ¡DATO CRÍTICO!
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Equipo registrado correctamente"})
    except Exception as e:
        return jsonify({"mensaje": f"Error: {str(e)}"}), 400

# --- NUEVA RUTA: CREAR CLIENTE ---
@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    datos = request.json
    try:
        nuevo_cliente = Cliente(
            nombre=datos['nombre'],
            direccion=datos.get('direccion', 'Sin dirección')
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({"mensaje": "Cliente creado exitosamente"})
    except Exception as e:
        return jsonify({"mensaje": f"Error: {str(e)}"}), 400
# C. Editar Equipo (Update)
@app.route('/api/equipos/<int:id>', methods=['PUT'])
def actualizar_equipo(id):
    equipo = Equipo.query.get(id)
    if not equipo: return jsonify({"mensaje": "No encontrado"}), 404
    
    datos = request.json
    equipo.nombre = datos['nombre']
    equipo.tipo = datos['tipo']
    equipo.serial = datos['serial']
    equipo.ubicacion = datos['ubicacion']
    equipo.observaciones = datos.get('observaciones', '')
    equipo.estado = datos.get('estado', equipo.estado)
    # También podemos mover un equipo de cliente si quisiéramos
    if 'cliente_id' in datos:
        equipo.cliente_id = int(datos['cliente_id'])

    db.session.commit()
    return jsonify({"mensaje": "Equipo actualizado"})

# D. Eliminar Equipo
@app.route('/api/equipos/<int:id>', methods=['DELETE'])
def eliminar_equipo(id):
    equipo = Equipo.query.get(id)
    if equipo:
        db.session.delete(equipo)
        db.session.commit()
    return jsonify({"mensaje": "Eliminado"})

# --- 5. REPORTES PDF (Con Cliente) ---
# Asegúrate de importar 'request' arriba si no está: 
# from flask import request

@app.route('/exportar-pdf')
def exportar_pdf():
    # 1. RECIBIMOS EL FILTRO (Igual que en el Dashboard)
    cliente_id = request.args.get('cliente_id')
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setTitle("Reporte de Mantenimiento")

    # 2. DEFINIR EL TÍTULO SEGÚN EL FILTRO
    titulo_reporte = "Reporte Global de Activos"
    subtitulo = "Listado General"
    
    equipos = []

    if cliente_id:
        # Si hay filtro, buscamos el cliente y sus equipos
        cliente = Cliente.query.get(cliente_id)
        if cliente:
            titulo_reporte = f"Cliente: {cliente.nombre}" # <--- EL CLIENTE VA AL TÍTULO
            subtitulo = f"Sede: {cliente.direccion or 'Principal'}"
            equipos = cliente.equipos # Solo equipos de este cliente
    else:
        # Si no hay filtro, traemos todo
        equipos = Equipo.query.all()

    # --- DIBUJAR ENCABEZADO ---
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, titulo_reporte) # Título Grande
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 735, subtitulo)
    
    c.setStrokeColor(colors.black)
    c.line(50, 725, 550, 725)

    # --- CUERPO DEL REPORTE ---
    y = 660  # Altura inicial
    
    for equipo in equipos:
        # Salto de página si se acaba el espacio
        if y < 100:
            c.showPage()
            # Repetimos encabezado simple en nueva página
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, 750, f"Continuación: {titulo_reporte}")
            c.line(50, 740, 550, 740)
            y = 700

        # 1. QR (Izquierda)
        contenido_qr = f"ID:{equipo.id}\nSN:{equipo.serial}"
        qr = qrcode.QRCode(box_size=5, border=1)
        qr.add_data(contenido_qr)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        img_qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        c.drawImage(ImageReader(qr_buffer), 50, y, width=50, height=50)

        # 2. DATOS DEL EQUIPO (Derecha)
        # NOTA: YA NO DIBUJAMOS LA LÍNEA "CLIENTE: ..." AQUÍ
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120, y + 35, f"{equipo.nombre}") # Nombre del equipo destacado
        
        c.setFont("Helvetica", 10)
        c.drawString(120, y + 20, f"Tipo: {equipo.tipo} | Serial: {equipo.serial}")
        c.drawString(120, y + 5, f"Ubicación: {equipo.ubicacion}")

        # Observaciones
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.gray)
        obs = equipo.observaciones if equipo.observaciones else ""
        c.drawString(120, y - 8, f"Obs: {obs}")
        c.setFillColor(colors.black)

        # Estado (A la derecha)
        if equipo.estado == "Falla":
            c.setFillColor(colors.red)
        else:
            c.setFillColor(colors.green)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(450, y + 35, equipo.estado)
        c.setFillColor(colors.black)

        # Línea divisoria suave
        c.setStrokeColor(colors.lightgrey)
        c.line(50, y - 15, 550, y - 15)

        y -= 80 # Menos espacio porque quitamos una línea de texto

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="reporte_mantenimiento.pdf", mimetype='application/pdf')

# --- MIGRACIÓN (Ya la usaste) ---
@app.route('/setup-fase2')
def setup_fase2():
    # ... (El mismo código que ya pegaste antes) ...
    return "Setup listo (Ya lo corriste)"

if __name__ == '__main__':
    app.run(debug=True, port=5000)