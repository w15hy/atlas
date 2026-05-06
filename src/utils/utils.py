def ofile(file):
    with open(file, "r") as file:
        content = file.read()
        return content


def ofilelines(file):
    with open(file, "r") as file:
        content = file.readlines()
        return content


def wfilelines(file, lineas):
    with open(file, "w", encoding="utf-8") as f:
        f.writelines(lineas)


def wfile(tok):
    with open("tokens.txt", "a", encoding="utf-8") as f:
        f.write(f"{tok}\n")
