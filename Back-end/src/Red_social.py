from flask import Flask, flash, render_template, request, redirect, url_for, send_file, session
from flask_mail import Mail, Message
import os
import io
from flask_caching import Cache
from itsdangerous import URLSafeTimedSerializer, BadSignature
import database as db


#Declarar una variables donde estará nuestra carpeta principal  "Prueba flask"
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
#Unir src y templates a la carpeta de proyectos
template_dir = os.path.join(template_dir, 'src' ,  'templates')

#Una varaibles para inicializar flask  
app = Flask(__name__, template_folder = template_dir)

# Configuración de la caché
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

#------------configuracion de correos-------------#
app.config.update(dict(                     #
    DEBUG = True,                           #
    MAIL_SERVER = 'smtp.gmail.com',         #
    MAIL_PORT = 587,                        # Configuramos la smtp gratis de gmail
    MAIL_USE_TLS = True,                    #   
    MAIL_USE_SSL = False,                   #
    MAIL_USERNAME = 'mariojuancho23@gmail.com',                #
    MAIL_PASSWORD = 'dxpw mojl mfmx ekqb',             #
))

# Inicializar el servidor de correos
mail = Mail(app)

# Configurar la clave secreta para sesiones
app.secret_key = 'Clavesecreta23'


#Rutas de la aplicación, se pone / para que con el propio nombre de la app acceda el index
@app.route('/')
@cache.cached(timeout=3600)  # Almacena en caché durante 1 hora (ajusta el tiempo según tus necesidades)
def home():
        #Crear un cursor apra acceder a la base de datos
        cursor = db.database.cursor()
        #Hacer la consulta select
        cursor.execute("SELECT * FROM users")
        myresult = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject = []
        columnNames = [colum[0] for colum in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()

    #-----------PUBLICACION INICIALIZACION----------#
        #Crear un cursor apra acceder a la base de datos
        cursor2 = db.database.cursor()    
        #Hacer la consulta select
        cursor2.execute("SELECT * FROM articles")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2 = [colum[0] for colum in cursor2.description]
        for record in myresult2:
            insertObject2.append(dict(zip(columnNames2, record)))
        cursor2.close()

    #-----------SUBIDA DE IMAGENES INICIALIZACION-------------#
        cursor3 = db.database.cursor()
        cursor3.execute("SELECT id, nombre FROM imagenes")
        imagenes = cursor3.fetchall()
        cursor3.close()

    #-----------Esta es la renderizacion de todo-----------------------#
        return render_template ('index.html', data=insertObject, data2=insertObject2, imagenes=imagenes)
# ------------VERIFICACION DE CORREO Y LOGIN--------------------------#
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        cursor = db.database.cursor(dictionary=True)  # Configura el cursor para devolver resultados como diccionarios
        sql = "SELECT * FROM users WHERE correo = %s AND password = %s"
        data = (correo, password)
        cursor.execute(sql, data)
        user = cursor.fetchone()
        cursor.close()
        
        # Obtén el ID del usuario de la sesión
        user_id = session.get('user_id')
        
        if user is not None:
            session['user_id'] = user['id']

            # Enviar un mensaje de correo electrónico después de iniciar sesión
            msg = Message('Inicio de sesión exitoso', sender='tu_correo@gmail.com', recipients=[user['correo']])
            msg.body = '¡Bienvenido! Has iniciado sesión en nuestra aplicación.'
            mail.send(msg)

            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('publicaciones'))
        else:
            flash('Credenciales incorrectas', 'error')

    return render_template('login.html')

@app.route('/publicaciones')
def publicaciones():
    #Crear un cursor apra acceder a la base de datos
        cursor2 = db.database.cursor()    
        #Hacer la consulta select
        cursor2.execute("SELECT * FROM articles")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2 = [colum[0] for colum in cursor2.description]
        for record in myresult2:
            insertObject2.append(dict(zip(columnNames2, record)))
        cursor2.close()
        
        return render_template ('index_usuario.html', data2=insertObject2)

# ----------------Lógica para ingreso de datos de usuario---------------#
# Ruta para guardar usurarios en la base de datos
@app.route('/addUser', methods=['GET', 'POST'])
def addUser():
    if request.method == 'POST':
        name = request.form["name"]
        apellido_paterno = request.form["apellido_paterno"]
        apellido_materno = request.form["apellido_materno"]
        telefono = request.form["telefono"]
        cumpleanos = request.form["cumpleanos"]
        correo = request.form["correo"]
        username = request.form["username"]
        password = request.form["password"]

        cursor = db.database.cursor()
        # Verificar si el correo ya existe en la base de datos
        cursor.execute("SELECT id FROM users WHERE correo = %s", (correo,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Este correo ya está registrado. Por favor, usa otro correo para registrarte.', 'error')
        elif username and name and password:
            sql = "INSERT INTO users (name, apellido_paterno, apellido_materno, telefono, cumpleanos, correo, username, password ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            data = (name, apellido_paterno, apellido_materno, telefono, cumpleanos, correo, username, password)
            cursor.execute(sql, data)
            db.database.commit()

            # Envío de correo de confirmación
            serializer = URLSafeTimedSerializer(app.secret_key)
            confirmation_token = serializer.dumps(correo, salt='email-confirm-key')
            confirmation_link = url_for('confirm_account', token=confirmation_token, _external=True)
            msg = Message('Confirma tu cuenta', sender='tu_correo@gmail.com', recipients=[correo])
            msg.body = f'Por favor, haz clic en el siguiente enlace para confirmar tu cuenta: {confirmation_link}'
            mail.send(msg)

            flash('Se ha enviado un correo de confirmación a tu dirección. Por favor, verifica tu correo para activar tu cuenta.', 'success')

    return render_template('registro.html')

# Ruta para confirmar la cuenta
@app.route('/confirm/<token>', methods=['GET'])
def confirm_account(token):
    try:
        serializer = URLSafeTimedSerializer(app.secret_key)
        correo = serializer.loads(token, salt='email-confirm-key', max_age=3600)  # El token es válido durante 1 hora

        # Marcar la cuenta como confirmada en tu base de datos (por ejemplo, estableciendo un campo "confirmado" en la tabla de usuarios)

        flash('Tu cuenta ha sido confirmada con éxito. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    except BadSignature:
        flash('El enlace de confirmación es inválido o ha caducado.', 'error')
        return redirect(url_for('login'))
    
#Ruta para renderizar la pagina de perfil
@app.route('/perfil', methods=['GET'])
def perfil():
        #Crear un cursor apra acceder a la base de datos
        cursor = db.database.cursor()    
        #Hacer la consulta select
        cursor.execute("SELECT * FROM users")
        myresult2 = cursor.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2 = [colum[0] for colum in cursor.description]
        for record in myresult2:
            insertObject2.append(dict(zip(columnNames2, record)))
        cursor.close()   
        return render_template('perfil.html', data=insertObject2)

#Ruta para renderizar la pagina de blog
@app.route('/blog', methods=['GET'])
def blog():   
    return render_template('blog.html')

#Ruta para renderizar la pagina de blog registrado
@app.route('/registradoblog')
def registradoblog():   
    #Crear un cursor apra acceder a la base de datos
        cursor2 = db.database.cursor()    
        #Hacer la consulta select
        cursor2.execute("SELECT * FROM articles")
        myresult2 = cursor2.fetchall()
        #Convertir los datos a diccionario
        insertObject2 = []
        columnNames2 = [colum[0] for colum in cursor2.description]
        for record in myresult2:
            insertObject2.append(dict(zip(columnNames2, record)))
        cursor2.close()
        
        return render_template ('blog_usuario.html', data2=insertObject2)

#Ruta para renderizar la pagina de home
@app.route('/inicio', methods=['GET'])
def inicio():   
    return render_template('index.html')

#Ruta para cerrar sesion
@app.route('/cerrar_sesion', methods=['GET'])
def cerrar_sesion():   
    return render_template('index.html')

#Ruta para renderizar la pagina de home registrado
@app.route('/registradoinicio', methods=['GET'])
def registradoinicio():   
    return render_template('index_usuario.html')

#Ruta para eliminar los datos de los usurarios en la base de datos
@app.route("/delete/<string:id>")
def delete(id):
    cursor= db.database.cursor()
    sql = "DELETE FROM users WHERE id=%s"
    data = (id,)
    cursor.execute(sql,data)
    db.database.commit()
    return redirect(url_for("perfil"))
#Ruta para editar los datos de los usurarios en la base de datos
@app.route("/edit/<string:id>", methods=['POST'])
def edit(id):
    name = request.form["name"]
    apellido_paterno = request.form["apellido_paterno"]
    apellido_materno = request.form["apellido_materno"]
    telefono = request.form["telefono"]
    cumpleanos = request.form["cumpleanos"]
    correo = request.form["correo"]
    username = request.form["username"]
    password = request.form["password"]

    if username and name and password:
        cursor= db.database.cursor()
        sql = "UPDATE users SET name=%s, apellido_paterno=%s, apellido_materno=%s, telefono=%s, cumpleanos=%s, correo=%s, username=%s, password=%s WHERE id =%s"
        data = (name, apellido_paterno, apellido_materno, telefono, cumpleanos, correo, username, password,id)
        cursor.execute(sql,data)
        db.database.commit()
    return redirect(url_for("perfil"))

#--------PUBLICACION LOGICA-------------#
# Ruta para guardar artículos en la base de datos
@app.route("/add_article", methods=["POST"])
def add_article():
    title = request.form["title"]
    content = request.form["content"]
    
    if title and content:
        cursor2 = db.database.cursor()
        sql2 = "INSERT INTO articles (title, content) VALUES (%s, %s)"
        data2 = (title, content)
        cursor2.execute(sql2, data2)
        db.database.commit()
    cache.clear()
    return redirect(url_for("publicaciones"))

# Ruta para eliminar artículos de la base de datos
@app.route("/delete_article/<string:id>")
def delete_article(id):
    cursor2 = db.database.cursor()
    sql2 = "DELETE FROM articles WHERE id=%s"
    data2 = (id,)
    cursor2.execute(sql2, data2)
    db.database.commit()
    cache.clear()
    return redirect(url_for("publicaciones"))

# Ruta para editar artículos en la base de datos
@app.route("/edit_article/<string:id>", methods=['POST'])
def edit_article(id):
    title = request.form["title"]
    content = request.form["content"]
    
    if title and content:
        cursor2 = db.database.cursor()
        sql2 = "UPDATE articles SET title=%s, content=%s WHERE id=%s"
        data2 = (title, content, id)
        cursor2.execute(sql2, data2)
        db.database.commit()
    cache.clear()
    return redirect(url_for("publicaciones"))

#---------SUBIR IMAGEN-----------#
@app.route('/subir', methods=['POST'])
def subir_imagen():
    if request.method == 'POST':
        imagen = request.files['imagen']
        nombre = request.form['nombre']

        if imagen:
            cursor3 = db.database.cursor()
            cursor3.execute("INSERT INTO imagenes (nombre, imagen) VALUES (%s, %s)", (nombre, imagen.read()))
            db.database.commit()
            cursor3.close()
            return redirect(url_for('home'))

@app.route('/mostrar/<int:id>')
def mostrar_imagen(id):
    cursor3 = db.database.cursor()
    cursor3.execute("SELECT nombre, imagen FROM imagenes WHERE id = %s", (id,))
    result = cursor3.fetchone()
    cursor3.close()

    if result:
        nombre, imagen_bytes = result
        return send_file(
            io.BytesIO(imagen_bytes),
            mimetype='image/jpeg',  # Cambia 'image/jpeg' al tipo MIME correcto de tu imagen
            as_attachment=False,
            download_name=f"{nombre}.jpg"  # Cambia la extensión del archivo si es necesario
        )
    else:
        return "Imagen no encontrada"
    
if __name__ =='__main__':
    app.run(debug=True, port=4000)