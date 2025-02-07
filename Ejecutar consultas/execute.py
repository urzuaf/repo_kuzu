import subprocess
import argparse
import time

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
    lastQuerie = "x"
    try:
        results = []
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        lastQuerie = line
                        results.append(processQuerie(line))
                    except:
                        results.append('Error en linea' + lastQuerie)
                        print('Error en linea' + lastQuerie)
        for i in range(len(results)):
            results[i] = str(i + 1)+ "|" + results[i] + "\n"
        save(results, outputFile)
    except FileNotFoundError:
        print("Archivo no encontrado")
    except Exception as e:
        print("Error al leer el archivo ", e, "Ultima consulta ejecutada: ", lastQuerie )


def save(results, file_path):
    with open(file_path, "w") as ofile:
        ofile.writelines(results)

def processQuerie(querie):
    #Ejecutar 3 veces 
    lower = 1000000

    print("Executing: " + querie)

    # Correr una vez extra para calcular el timepo con python
    inicio = time.time()
    command = "echo \" "+ "call timeout=" + str(timeout) + "; "+ querie * 3 + " \" | " + kuzu_path + " --no_progress_bar "

    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    fin = time.time()
    pythonTime = fin - inicio

    res = str(result.stdout)
    err = str(result.stderr)
    lns = res.splitlines()


    if "core" in err:
        print("FATAL ERROR")
        count=0
        lower = "CORE DUMPED"
    elif "memory" in lns[-1]:
        print("Buffer")
        count= 0
        lower = "Memory limit"
 
    elif "Error" in lns[-1]:
        print("TIMEOUT REACHED")
        count= 0
        lower = "TIMEOUT"

    # Si encontramos problemas, no las volveremos a ejecutar
    if isinstance(lower, int):
        count = lns[-3]
        count = count.replace("'", "")
        count = count.replace("(", "")
        count = count.replace(")", "")
        count = count.split(" ")[0]
        count = int(count)

        times = []
        for idx,tt in enumerate(lns):
            if "Time" in tt:
                times.append(lns[idx])

        #No considerar el primer tiempo que es el de setear el timeout

        times = times[1:]
        for timei in times: 
            ts = timei.split("ms")
            compilingTime = float(ts[0].split(" ")[-1])
            executingTime = float(ts[1].split(" ")[-1])
            totalTime = round((compilingTime + executingTime)/1000,3)
            
            if(totalTime < lower):
                lower = totalTime

    print(querie + "|COUNT|" + str(count) + "|TIME|" + str(lower) + "|pythonTime|" + str(pythonTime))   
    return querie + "|COUNT|" + str(count) + "|TIME|" + str(lower) + "|pythonTime|" + str(pythonTime)

print("Executing queries from the input file")

openFile(inputFile)

print("DONE")
print("Results printed to: ", outputFile)

