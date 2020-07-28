import os 

def getFilesFromDirTree(dirName: str) -> list:
    """Funkcia na scan dir tree a získanie všetkých file.

    Funkcia používa os.walk, input parameter je root dir v ktorej má začať.
    Vráti všetky súbory ktoré sa nachádzajú v štruktúre pod touto dir ako relatívnu cestu od root dir
    """

    files = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        files += [os.path.join(dirpath, file) for file in filenames]

    return files