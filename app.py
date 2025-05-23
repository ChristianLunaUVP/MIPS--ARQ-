from flask import Flask, render_template, request
from mips_utils import procesar_instruccion

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    error = None
    if request.method == 'POST':
        instruccion = request.form['instruccion']
        resultado = procesar_instruccion(instruccion)
        if 'error' in resultado:
            error = resultado['error']
            resultado = None
    return render_template('index.html', resultado=resultado, error=error)

if __name__ == '__main__':
    app.run(debug=True)
