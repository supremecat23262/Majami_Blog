from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_caching import Cache
import database as db
import io
import mysql.connector
import time

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # Usa una caché simple en memoria

# Función para obtener una conexión a la base de datos
def get_database_connection():
    try:
        if not hasattr(get_database_connection, 'connection'):
            get_database_connection.connection = db.database
        # Intenta ejecutar una consulta simple para verificar la conexión
        print("Intentando establecer la conexión a la base de datos...")
        cursor = get_database_connection.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()  # Leer el resultado
        cursor.close()
        print("Conexión establecida con éxito.")
        return get_database_connection.connection
    except mysql.connector.Error as err:
        # Si se produce un error de MySQL, espera un tiempo antes de volver a intentar
        print(f"Error de conexión: {err}")
        time.sleep(5)
        print("Intentando nuevamente...")
        return get_database_connection()
    
@app.route('/')
def index():
    connection = get_database_connection()  # Obtiene una conexión
    cursor4 = connection.cursor()
    cursor4.execute("SELECT id, nombre FROM iconos")
    iconos = cursor4.fetchall()
    cursor4.close()
    return render_template('subir_imagen.html', iconos=iconos)

@app.route('/subir', methods=['POST'])
def subir_imagen():
    if request.method == 'POST':
        nombres = request.form.getlist('nombre')
        imagenes = request.files.getlist('imagen')

        for nombre, imagen in zip(nombres, imagenes):
            if imagen:
                cursor4 = db.database.cursor()
                cursor4.execute("INSERT INTO iconos (nombre, imagen) VALUES (%s, %s)", (nombre, imagen.read()))
                db.database.commit()
                cursor4.close()

        # Borra la caché después de subir una imagen para que la página se actualice correctamente
        cache.clear()
        
        return redirect(url_for('index'))

@app.route('/mostrar/<int:id>')
@cache.cached(timeout=3600)  # Almacena en caché la imagen durante 1 hora (ajusta según sea necesario)
def mostrar_imagen(id):
    cursor4 = db.database.cursor()
    cursor4.execute("SELECT nombre, imagen FROM iconos WHERE id = %s", (id,))
    result = cursor4.fetchone()
    cursor4.close()

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
    app.run(debug=True, port=400)