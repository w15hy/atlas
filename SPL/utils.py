def ofile(file):
    with open(file, "r", encoding="utf-8") as file:
        content = file.read()
        return content

def ofilelines(file):
    with open(file, "r", encoding="utf-8") as file:
        content = file.readlines()
        return content

def wfilelines(file, content):
    with open(file, "w", encoding="utf-8") as f:
        if isinstance(content, str):
            f.write(content)
        else:
            f.writelines(content)
