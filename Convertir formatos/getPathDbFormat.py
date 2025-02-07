import subprocess
import os
import argparse

# Configurar argparse para manejar los argumentos
parser = argparse.ArgumentParser(description="Ejecutar consultas en Kuzu Database.")
parser.add_argument("-k", "--kuzu_path", default="./kuzu", help="Ruta al ejecutable de Kuzu.")
parser.add_argument("-d", "--database_path", default="./database", help="Ruta a la base de datos.")
parser.add_argument("-i", "--input_file", default="input", help="Archivo de entrada con las consultas.")
parser.add_argument("-o", "--output_folder", default="output", help="Archivo de salida para los resultados.")
parser.add_argument("-t", "--timeout", type=int, default=1000, help="Tiempo límite para ejecutar cada consulta (ms).")

# Parsear los argumentos
args = parser.parse_args()

# Variables clave
kuzu_path = f"{args.kuzu_path} {args.database_path}"
inputFile = args.input_file
outputFolder = args.output_folder
timeout = args.timeout


#Leer las consultas desde un archivo
def openFile(file_path):
    lastQuerie = "x"
    count = 1
    try:
        results = []
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    lastQuerie = line
                    processQuerie(count,line)
                    count += 1

    except FileNotFoundError:
        print("Archivo no encontrado")
    except Exception as e:
        print("Error al leer el archivo ", e, "Ultima consulta ejecutada: ", lastQuerie )

def processQuerie(index, querie):
    print("Executing: " + querie)

    # Agregamos esto, necesario para la salida
    querie = querie.replace("return p", "return properties(nodes(p), 'id'), properties(rels(p), '_LABEL')")

    command = "echo \" "+ "call timeout=" + str(timeout) + "; "+ querie + " \" | " + kuzu_path + " --no_progress_bar -m csv"
    result = subprocess.run(command, shell=True, text=True, capture_output=True)

    res = str(result.stdout)
    err = str(result.stderr)
    lns = res.splitlines()
    tmp = lns[7:-3]
    out = []

    if "core" in err:
        print("FATAL ERROR")
        out = ["CORE DUMPED\n"]
        

    elif "Interrupted" in lns[-1]:
        print("TIMEOUT REACHED")
        out = ["TIMEOUT\n"]
       
    elif "memory" in lns[-1]:
        print("Memory Limit")
        out = ["Memory limit\n"]
    else:
        for id,o in enumerate(tmp):
            parts = o.split('","')
            #Si solo tienen una relación entran aqui
            if(len(parts) < 2):
                parts = parts[0].split('",')
            #Si no tienen relación y es consulta ? entran aquí
            if(len(parts) < 2):
                parts = parts[0].split(',')
            nodes = parts[0].strip('"[]').split(',')
            relationships = parts[1].strip('"[]').split(',')
            intercalated = ""

            for idx, i in enumerate(relationships):
                intercalated += " "+ nodes[idx]
                intercalated += " "+ relationships[idx]


            intercalated += " " + nodes[-1] + "\n"
            intercalated = intercalated.replace("'", "")
            out.append(intercalated)

    save(str(index), out)

def save( archivo, resultado):
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    ruta = os.path.join(outputFolder, archivo)
    with open(ruta, "w") as ofile:
        ofile.writelines(resultado)
    print("saved on " + archivo)

   

#Conexion a la base de datos
print("Executing queries from the input file")
openFile(inputFile)
print("Queries executed")
print("Results printed to: ", outputFolder)
print("DONE")