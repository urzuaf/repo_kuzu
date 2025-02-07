import csv

from collections import defaultdict

archivo = "Edges.csv"

relaciones = defaultdict(list)

with open(archivo, mode = "r", newline= "", encoding="utf-8") as entrada:
    lector_csv = csv.reader(entrada)
    for fila in lector_csv:
        if len(fila) == 3:
            x1, relacion,x2 = fila
            relaciones[relacion].append((x1,x2))

for relacion, nodos in relaciones.items():
    nombre_archivo = f'{relacion}.csv'
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as salida:
        escritor_csv = csv.writer(salida)
        escritor_csv.writerow(['from', 'to'])
        escritor_csv.writerows(nodos)

print("Archivos Generados")


