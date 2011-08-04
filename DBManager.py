import sys
import yum
import MySQLdb

sys.path.append('/usr/share/yum-cli')
from output import *
from yumcommands import *
from cli import *
from datetime import datetime

modTypes = {'insert':'Init','removed':'Removed', 'restored' :'Restored', 'modified' :'Modified'}
textInsert = 'First time insertion of package'
textMod= 'The version or release has being modified'
textMissDepGroup = 'Unavailable'


class DBManager:
    def __init__(self):
        try:
            self.db=MySQLdb.connect(host="144.174.63.107",user="olmozavala",passwd="sopasperico",db="hpc_data")
        except MySQLdb.Error, e:
            print "Error: %s" % e.args[1]
            sys.exit(1)

        self.cursor = self.db.cursor()

    def commit(self):
        self.db.commit()

    def close(self):
        """ Closes the database connection"""
        self.db.commit()
        self.db.close()

    def clearAllTables(self):
        """Deletes all the records in the tables and initializes the groups table. """ 
        try:
            print "Clearing table softwareversion..."
            self.cursor.execute("DELETE FROM ac_softwaremod")
        except MySQLdb.Error, e:
            print "Error Deleting softwaremod: %s"%e.args[1]

        try:
            print "Clearing table softwaredepen..."
            self.cursor.execute("DELETE FROM ac_softwaredepen")
        except MySQLdb.Error, e:
            print "Error Deleting software depen: %s"%e.args[1]

        try:
            print "Clearing table softwareitem..."
            self.cursor.execute("DELETE FROM ac_softwareitem")
        except MySQLdb.Error, e:
            print "Error Deleting software version: %s"%e.args[1]

        try:
            print "Clearing table softwaretype..."
            self.cursor.execute("DELETE FROM ac_softwaretype")
        except MySQLdb.Error, e:
            print "Error Deleting software version: %s"%e.args[1]

        try:
            self.cursor.execute(" INSERT INTO ac_softwaretype (name,description) VALUES(%s,'This type of "+
                                " packages has some dependency that can''t be found. In the notes of these packages should be "+
                                " the list of dependencies that can''t be found')  ", (textMissDepGroup))

        except MySQLdb.Error, e:
            print "ERROR: %s" % e.args[1]
        self.db.commit()

    def pkgFromName(self,name):
        """ Returns all the package info from a name"""
        try:
            #self.cursor.execute("""SELECT id,name,pk_version,pk_release FROM ac_softwareitem WHERE name=%s""",name)
            self.cursor.execute("""SELECT * FROM ac_softwareitem WHERE name=%s""",name)
            pkg = self.cursor.fetchone()
        except MySQLdb.Error, e:
            print "Warning: Package not found. %s" % e.args[1]
            sys.exit(1)

        return pkg

    def idFromPkgName(self,name):
        """ Obtains the id for a package name"""
        try:
            self.cursor.execute("""SELECT id FROM ac_softwareitem WHERE name=%s""",name)#Obtain id from DB
        except MySQLdb.Error, e:
            print "Error: %s" % e.args[1]
            sys.exit(1)

        return self.cursor.fetchone()

    def insertPkg(self,name, desc,summary, version, release, available):
        """ Inserts a new package into the database"""
        try:
            #TODO update the available field ( is not taken from the inputs)
            self.cursor.execute(""" INSERT INTO ac_softwareitem (name,description,summary,
                            pk_version,pk_release,available) VALUES (%s,%s,%s,%s,%s,true) """,
                (name,desc,summary,version,release))

        except MySQLdb.Error, e:
            print "ERROR Inserting new package: %s" % e.args[1]

    def insertModif(self, str_now,mod_type, notes, fkpkg):
        """ Inserts a new modification made into a Packages"""
        try:
            self.cursor.execute(""" INSERT INTO ac_softwaremod (mod_date,mod_type,mod_notes,fk_softwareitem)
                             VALUES (%s,%s,%s,%s) """, (str_now,mod_type,notes,fkpkg))
        except MySQLdb.Error, e:
            print "ERROR Inserting modification of new package: %s" % e.args[1]

    def insertDepen(self, pkg, depen):
        try:
            self.cursor.execute(""" INSERT INTO ac_softwaredepen VALUES (%s,%s) """, (pkg,depen))

        except MySQLdb.Error, e:
            x = 1
            #print "ERROR inserting a dependency: %s" % e.args[1]
            #print "The current relation (pkg -> dependency) already exists: %s" % e.args[1]


    def updatePkg(self, id, newver, newrelease, newdesc, newsum):
        """ Updates a package by id"""
        try:
            # Updating the info of the package
            self.cursor.execute(""" UPDATE ac_softwareitem SET 
                                pk_version=%s, pk_release=%s, description=%s, summary=%s
                                 WHERE id=%s """,(newver,newrelease,newdesc,newsum,id))

        except MySQLdb.Error, e:
            print "ERROR: %s" % e.args[1]
