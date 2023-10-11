from flask import Flask, render_template, request, redirect, url_for, send_file
import database as db
import io

# Declarando nombre de la aplicación e inicializando
app = Flask(__name__)

@app.route('/')
def index():
    cursor4 = db.database.cursor()
    cursor4.execute("SELECT id, nombre FROM iconos")
    iconos = cursor4.fetchall()
    cursor4.close()
    return render_template('subir_imagen.html', iconos=iconos)

@app.route('/subir', methods=['POST'])
def subir_imagen():
    if request.method == 'POST':
        imagen = request.files['imagen']
        nombre = request.form['nombre']

        if imagen:
            cursor4 = db.database.cursor()
            cursor4.execute("INSERT INTO iconos (nombre, imagen) VALUES (%s, %s)", (nombre, imagen.read()))
            db.database.commit()
            cursor4.close()
            return redirect(url_for('index'))

@app.route('/mostrar/<int:id>')
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