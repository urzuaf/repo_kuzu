import argparse

parser = argparse.ArgumentParser(description="Convertir consultas formato pathdb a kuzu.")
parser.add_argument("-i", "--input_file", default="input", help="Archivo de entrada con las consultas.")
parser.add_argument("-o", "--output_file", default="output", help="Archivo de salida para los resultados.")

args = parser.parse_args()

inputFile = args.input_file
outputFile = args.output_file

def parse(input_file, output_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                line = line.strip().split("\t")
                start = "match p = (n : node {id: '" + line[0] + "'})-[:"
                end = "] -> () return p limit 100;\n"
                between = ""
                for i in line[1]:
                    # quitamos los parentesis que estorvan xd
                    i = i.replace("(", "")
                    i = i.replace(")", "")
                    if (i == '.'):
                        between += "]->()-[:"
                    elif (i == '*'):
                        between += "* 0..4"
                    elif (i == '+'):
                        between += "* 1..4"
                    elif (i == '?'):
                        between += "* 0..1"
                    else:
                        between += i
                out = start + between + end
                outfile.write(out)
        print(f"File '{input_file}' successfully parsed to '{output_file}'.")
    except FileNotFoundError:
        print(f"File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

parse(inputFile, outputFile)