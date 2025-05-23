from flask import Flask, render_template, request
from mips_utils import procesar_instruccion

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        instruccion = request.form['instruccion']
        resultado = procesar_instruccion(instruccion)
    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
