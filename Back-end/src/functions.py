import database as db

def load_home_data():
    # Crear un cursor para acceder a la base de datos
    cursor = db.database.cursor()
    # Hacer la consulta select
    cursor.execute("SELECT * FROM users")
    myresult = cursor.fetchall()
    # Convertir los datos a un diccionario
    insertObject = []
    columnNames = [colum[0] for colum in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    # -----------PUBLICACION INICIALIZACIÓN----------#
    # Crear un cursor para acceder a la base de datos
    cursor2 = db.database.cursor()
    # Hacer la consulta select
    cursor2.execute("SELECT * FROM articles")
    myresult2 = cursor2.fetchall()
    # Convertir los datos a un diccionario
    insertObject2 = []
    columnNames2 = [colum[0] for colum in cursor2.description]
    for record in myresult2:
        insertObject2.append(dict(zip(columnNames2, record)))
    cursor2.close()

    # -----------SUBIDA DE IMÁGENES INICIALIZACIÓN-------------#
    cursor3 = db.database.cursor()
    cursor3.execute("SELECT id, nombre FROM imagenes")
    imagenes = cursor3.fetchall()
    cursor3.close()

    return insertObject, insertObject2, imagenes
