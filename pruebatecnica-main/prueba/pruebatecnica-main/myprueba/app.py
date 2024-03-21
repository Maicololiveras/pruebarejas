# Importar Flask para crear la aplicación web
from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np


# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)
# Definir datos de fabricación
largo_reja = 2.5
alturas = {1: 1.03, 2: 1.53, 3: 2.03}
fijadores = {1: 3, 2: 4, 3: 6}
pinturas = {0: "sin pintura", 1: "blanca", 2: "negra", 3: "verde"}

# Definir función para calcular la cantidad de componentes
def calcular_cantidad(largo_total, altura, color):
    cantidad_rejas = int(largo_total / largo_reja)
    cantidad_postes = cantidad_rejas * 2
    cantidad_tornillos = cantidad_postes * 4
    cantidad_fijadores = fijadores[altura]
    return cantidad_rejas, cantidad_postes, cantidad_tornillos, cantidad_fijadores, pinturas[color]

#Definir Función para dibujar imagen de rejas y guardarla en memoria como archivo
def dibujar_rejas(cantidad_rejas, altura):
    fig, ax = plt.subplots(figsize=(4, 5))

    # Dibujar los postes
    for i in range(cantidad_rejas * 2):
        ax.plot([i * largo_reja, i * largo_reja], [0, alturas[altura]], 'k-', linewidth=2)

    # Dibujar las rejas
    for i in range(cantidad_rejas):
        # Dibujar la parte superior de la reja
        x = np.linspace(i * largo_reja, (i + 1) * largo_reja, 100)
        y = np.sin(x * np.pi / largo_reja) * (alturas[altura] / 4) + alturas[altura] / 2
        ax.plot(x, y, 'k-', linewidth=2)

        # Dibujar la parte inferior de la reja
        y_bottom = y - alturas[altura] / 2
        ax.plot(x, y_bottom, 'k-', linewidth=2)

    ax.set_xlim(0, cantidad_rejas * largo_reja)
    ax.set_ylim(0, alturas[altura])
    ax.axis('off')  # Ocultar ejes

    # Guardar el diseño como una imagen en un buffer de Bytes
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0.1)  # Ajustar tamaño de la imagen
    img_bytes.seek(0)

    # Convertir la imagen a base64 para poder incrustarla directamente en el HTML
    encoded_img = base64.b64encode(img_bytes.read()).decode('utf-8')
    return encoded_img

# Definir ruta de inicio
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        largo_total = float(request.form['largo_total'])
        altura = int(request.form['altura'])
        color = int(request.form['color'])
        confirmado = request.form.get('confirmado', False)
        cantidad_rejas, cantidad_postes, cantidad_tornillos, cantidad_fijadores, color_pintura = calcular_cantidad(largo_total, altura, color)
        fecha_confirmacion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if confirmado:
            # Guardar los datos del pedido confirmado
            with open("pedidos_confirmados.txt", "a") as file:
                file.write(f"Fecha de confirmación: {fecha_confirmacion}, Largo total: {largo_total}, Altura: {alturas[altura]}, Color: {color_pintura}\n")
        img_bytes = dibujar_rejas(cantidad_rejas, altura) # Dibujar el diseño de las rejas y servirlo como una imagen
        return render_template('index.html', img_bytes=img_bytes, cantidad_rejas=cantidad_rejas, cantidad_postes=cantidad_postes, cantidad_tornillos=cantidad_tornillos, cantidad_fijadores=cantidad_fijadores, color_pintura=color_pintura)
    return render_template('index.html')


# Función para cargar los pedidos confirmados desde el archivo de texto
def cargar_pedidos_confirmados():
    with open('pedidos_confirmados.txt', 'r') as file:
        pedidos = [line.strip().split(',') for line in file.readlines()]
    return pedidos


# Definir ruta para ver pedidos confirmados
@app.route('/pedidos_confirmados')
def ver_pedidos_confirmados():
    # Cargar los pedidos confirmados
    pedidos = cargar_pedidos_confirmados()
    return render_template('pedidos_confirmados.html', pedidos=pedidos)

# Ruta para generar y mostrar el diagrama de las rejas
@app.route('/diagrama_rejas')
def diagrama_rejas():
    # Generar el diagrama
    cantidad_rejas = 10  # Ejemplo: cantidad de rejas (puedes obtener estos datos de tu base de datos o de algún otro lugar)
    nombres_rejas = ['Reja {}'.format(i+1) for i in range(cantidad_rejas)]
    cantidades = [3, 5, 2, 7, 4, 6, 8, 3, 2, 5]  # Ejemplo: cantidades de rejas (puedes obtener estos datos de tu base de datos o de algún otro lugar)

    # Crear el gráfico de barras
    plt.bar(nombres_rejas, cantidades)
    plt.xlabel('Reja')
    plt.ylabel('Cantidad')
    plt.title('Diagrama de Rejas Solicitadas por los Clientes')
    plt.xticks(rotation=45)

    # Guardar el gráfico en un buffer de Bytes
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    # Limpiar la figura de Matplotlib
    plt.clf()

    # Servir la imagen como un archivo
    return send_file(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)