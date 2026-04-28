from utils.utils import ofilelines
import re


# Test it out
file = "main.atl"
lines = ofilelines("programs/" + file)
dict_macros = {}

def define_macros():
    for idx,line in enumerate(lines):
        if "#define" in line:
            expr = line.strip().split()
            dict_macros.update({expr[1]:expr[2]})
            lines[idx] = ""
        elif line == "\n":
            lines[idx] = ""

def main():
    define_macros()
    for idx,linea in enumerate(lines):
        for key in dict_macros.keys():
            if key in linea:
                lines[idx] = linea.replace(key,dict_macros.get(key))
    print("".join(lines))
main()

# to implement
# SUMA\(\d+(\.\d+)?,\d+(\.\d+)?\)