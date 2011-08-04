import sys
import yum
import MySQLdb

sys.path.append('/usr/share/yum-cli')
from output import *
from yumcommands import *
from cli import *
from datetime import datetime
from Package import *

modTypes = {'insert':'Init','removed':'Removed', 'restored' :'Restored', 'modified' :'Modified'}
textInsert = 'First time insertion of package'
textMod= 'The version or release has being modified'
textMissDepGroup = 'Unavailable'
groupTypes = {'Una':'Missing Dependencies', 'Rem':'Removed'}


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
            print "Inserting default values for Group packages"
            
            name = groupTypes['Una']
            desc =  """This type of package has some dependencies that couldn''t be found on the repositories.
                     In the ''notes'' atribute of each package it should be  
                     the list of dependencies that couldn''t be found')  """
            self.insertPkgGroup(name,desc) 

            name = groupTypes['Rem']
            desc = "This packages were removed from the repositories and are currently unavailable"
            self.insertPkgGroup(name,desc) 
           
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

        if(pkg!=None): #Obtaining Package object
            Pkg = Package(pkg)
            return Pkg

        return None
        
    def idFromGroupName(self,name):
        """ Obtains the id for a package group, from its name"""
        try:
            self.cursor.execute("""SELECT id FROM ac_softwaretype WHERE name=%s""",name)#Obtain id from DB
        except MySQLdb.Error, e:
            print "ERROR Selecting id from group name: %s" % e.args[1]
            sys.exit(1)

        return self.cursor.fetchone()


    def idFromPkgName(self,name):
        """ Obtains the id for a package name"""
        try:
            self.cursor.execute("""SELECT id FROM ac_softwareitem WHERE name=%s""",name)#Obtain id from DB
        except MySQLdb.Error, e:
            print "ERROR selecting id from package name: %s" % e.args[1]
            sys.exit(1)

        return self.cursor.fetchone()

    def insertPkgToGroup(idpkg, groupName):
        """ Inserts one package to a package group (by name) """
        idgroup = self.idFromGroupName(groupName)
        try:
            self.cursor.execute(""" INSERT INTO ac_softwaretypeitem (id_item,id_type) VALUES (%s,%s) """,
                (idpkg,idgroup))

        except MySQLdb.Error, e:
            print "ERROR Inserting new package, group relationship: %s" % e.args[1]
            sys.exit(1)

    def insertPkgGroup(self,name,desc):
        """ Inserts a new package group"""
        try:
            self.cursor.execute(""" INSERT INTO ac_softwaretype (name,description) VALUES (%s,%s) """,
                (name,desc))

        except MySQLdb.Error, e:
            print "ERROR Inserting new package group: %s" % e.args[1]
            sys.exit(1)

    def insertPkg(self,name, desc,summary, version, release, available):
        """ Inserts a new package into the database"""
        try:
            #TODO update the available field ( is not taken from the inputs)
            self.cursor.execute(""" INSERT INTO ac_softwareitem (name,description,summary,
                            pk_version,pk_release,available) VALUES (%s,%s,%s,%s,%s,true) """,
                (name,desc,summary,version,release))

        except MySQLdb.Error, e:
            print "ERROR Inserting new package: %s" % e.args[1]
            sys.exit(1)

    def insertModif(self, str_now,mod_type, notes, fkpkg):
        """ Inserts a new modification made into a Packages"""
        try:
            self.cursor.execute(""" INSERT INTO ac_softwaremod (mod_date,mod_type,mod_notes,fk_softwareitem)
                             VALUES (%s,%s,%s,%s) """, (str_now,mod_type,notes,fkpkg))
        except MySQLdb.Error, e:
            print "ERROR Inserting modification of new package: %s" % e.args[1]
            sys.exit(1)

    def insertDepen(self, pkg, depen):
        try:
            self.cursor.execute(""" INSERT INTO ac_softwaredepen VALUES (%s,%s) """, (pkg,depen))

        except MySQLdb.Error, e:
            print "The current relation (pkg -> dependency) already exists: %s" % e.args[1]
            sys.exit(1)

    def updatePkg(self, id, ver, release, desc, sum, notes, avai):
        """ Updates a package by id"""
        try:
            # Updating the info of the package
            self.cursor.execute(""" UPDATE ac_softwareitem SET 
                                pk_version=%s, pk_release=%s, description=%s, summary=%s,
                                pk_notes=%s, available=%s
                                WHERE id=%s """,(ver,release,desc,sum, notes, avai,id))

        except MySQLdb.Error, e:
            print "ERROR Updating a package: %s" % e.args[1]
            sys.exit(1)
