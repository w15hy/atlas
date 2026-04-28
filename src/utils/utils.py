def ofile(file):
    with open(file, "r") as file:
        content = file.read()
        return content

def ofilelines(file):
    with open(file, "r") as file:
        content = file.readlines()
        return content
