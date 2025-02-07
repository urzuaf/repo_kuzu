import subprocess
import argparse
import time
import re

# Configurar argparse para manejar los argumentos
parser = argparse.ArgumentParser(description="Ejecutar consultas en Kuzu Database.")
parser.add_argument("-k", "--kuzu_path", default="./kuzu", help="Ruta al ejecutable de Kuzu.")
parser.add_argument("-d", "--database_path", default="./database", help="Ruta a la base de datos.")
parser.add_argument("-i", "--input_file", default="input", help="Archivo de entrada con las consultas.")
parser.add_argument("-o", "--output_file", default="output", help="Archivo de salida para los resultados.")
parser.add_argument("-t", "--timeout", type=int, default=1000, help="Tiempo límite para ejecutar cada consulta (ms).")

# Parsear los argumentos
args = parser.parse_args()

# Variables clave
kuzu_path = f"{args.kuzu_path} {args.database_path}"
inputFile = args.input_file
outputFile = args.output_file
timeout = args.timeout


#Leer las consultas desde un archivo
def openFile(file_path):
    try:
        linefiles = ""
        with open(file_path, "r") as file:
            for line in file:
                if line.strip() != "":
                    linefiles += line
            
        results = processQueries(linefiles)
        save(results, outputFile)
    except FileNotFoundError:
        print("Archivo no encontrado")


def save(results, file_path):
    with open(file_path, "w") as ofile:
        ofile.writelines(results)

def processQueries(queries):
    results = []
    print("ejecutando: ")
    print(queries)
    command = f"echo \" call timeout = {timeout} ;"+  queries * 4 + " \" | " + kuzu_path + " --no_progress_bar -m trash"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    print(result)
    print("aqui")

    res = str(result.stdout)
    err = str(result.stderr)
    lns = res.splitlines()
    save(lns,'allLines')
    print("DESDE AQUI #################################")
    for l in lns:
        #print(l)
        if  "Time" in l or "Buffer" in l or "Interrupted" in l:
            #ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            # Limpiar el texto
            #l = ansi_escape.sub("", l)
            results.append(l)
    
    
    newres = []
    contadordelineas = 1
    for i in queries.splitlines():
        if not i.strip() == "":
            contadordelineas += 1
    
    if contadordelineas > len(results):
        raise ValueError("contadordelineas es mayor que el tamaño de results")



    new2 = results[contadordelineas:]
    save(new2, 'resultadosintermedios')
    print("a borrar", contadordelineas)

    print("Resultados : ", len(results))
    print("new2: ", len(new2))

    newres = []

    for s in new2:
        print(s)
    
    for ll in new2:
        print(ll)
        if "Buffer" in ll:
            newres.append("Buffer" + '\n')
            continue
        if "Interrupted" in ll:
            newres.append("Interrupted" + '\n')
            continue
        if "Time" in ll:
            tmp = ll.split(",")[1]
            tmp = tmp.split("ms")[0]
            tmp = tmp.strip()
            newres.append(tmp + '\n')

    print("AQUI 1")
    print(newres)
    print("contadordelineas - 1: ", contadordelineas - 1)
    if contadordelineas - 1 > len(newres):
        raise ValueError("contadordelineas - 1 es mayor que el tamaño de newres")

    results = []
    for i in range(0, len(newres), contadordelineas - 1):
        ln = newres[i:i + contadordelineas - 1]
        results.append(ln)
            
    print("AQUI 2")

    if not results or any(len(row) != len(results[0]) for row in results):
        raise ValueError("results está vacío o tiene filas de longitud inconsistente")

    column_values = [[] for _ in range(len(results[0]))]

    print("AQUI 3")
    # Procesar cada fila del arreglo
    for row in results:
        for i, value in enumerate(row):
            value = value.strip()  # Eliminar espacios y saltos de línea
            if value != "Buffer" and value != "Interrupted":  # Ignorar "Buffer"
                column_values[i].append(float(value)/1000)  # Convertir a float y agregar
            else:
                column_values[i].append(value)

    print("AQUI 4")
    # Calcular los promedios
    result = []
    for values in column_values:
        if "Buffer" not in values and "Interrupted" not in values:  # Si la columna tiene valores numéricos
            
            result.append(sum(values) / len(values))
        else:
            result.append(values)  # Si no hay valores numéricos

    print("AQUI 5")
    string_data = [str(item) for item in result]
    indexed_data = [f"{i + 1}. {item}\n" for i, item in enumerate(string_data)]

    print("AQUI 6")
    return indexed_data


#Conexion a la base de datos
print("Executing queries from the input file")
openFile(inputFile)
print("Queries executed")
print("Results printed to: ", outputFile)
print("DONE")
