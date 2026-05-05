def ofile(file):
    with open(file, "r") as file:
        content = file.read()
        return content

def ofilelines(file):
    with open(file, "r") as file:
        content = file.readlines()
        return content

def wfilelines(file, content):
    with open(file, "w") as f:
        if isinstance(content, str):
            f.write(content)
        else:
            f.writelines(content)
