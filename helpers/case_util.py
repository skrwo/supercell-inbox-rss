# source: https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
# dumb but works for us
def split_camel_case(s: str):
    new_string = ""
    for i in s:
        if i.isupper():
            new_string += "*" + i
        else:
            new_string += i
    x = new_string.split("*")
    if "" in x:
        x.remove("")
    return x
