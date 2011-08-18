import sys

class Package:
    id = 0
    name = ""
    desc = ""
    srpm = ""
    summ = ""
    avai = ""
    version = ""
    release = ""
    notes = ""
    arch = ""

    def __init__(self, cpkg):
        self.id = cpkg[0]
        self.name = cpkg[1]
        self.desc = cpkg[2]
        self.summ = cpkg[3]
        self.srpm=  cpkg[4]
        self.avai = cpkg[5]
        self.version = cpkg[6]
        self.release = cpkg[7]
        self.notes = cpkg[8]
        self.arch = cpkg[9]



if __name__=="__main__":
    """Just an example"""
    arr = ['id0', 'nombre','descrip','summa','availa','version','release','notes','arch']
    pkg = Package(arr)
    print pkg.name
