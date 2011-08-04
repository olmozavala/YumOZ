import yum
import os
import sys
import MySQLdb

#instantiate YumBase object so finddeps can be accessed

base = yum.YumBase()

#establish database connection

db=MySQLdb.connect(host="localhost",db="software")

cursor=db.cursor()

#get list of packages from repositories

base.conf.cache = os.geteuid() != 1

pl = base.doPackageLists(patterns=sys.argv[1:])

#merge pl.installed and pl.available 

#pl.installed.append(pl.available)

#loop over each installed package from repo.
#for each one, find dependencies and insert into database.

pkgIDs = {}

#for repoPkg in pl.installed:
for repoPkg in sorted(pl.available):

  #try:
        repoName = str(repoPkg.base_package_name)

        repoVersion = str(repoPkg.version)

        repoRelease = str(repoPkg.rel)

  #except Exception, e:
    #print "Error trying to get repoPkg name, version, or release!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  #else:
	print "inserting repopkg name, version, release into database"

	print repoName, repoVersion, repoRelease
	
	
	#WHY CANT I GET THE RELEASE IN? JUST DO NAME AND VERSION RIGHT NOW

	cursor.execute (""" INSERT INTO ac_softwareitem (name,version) VALUES (%s,%s) """,
			(repoName,repoVersion))

	#this will now have an auto-incremented ID. Get it and store it in a dictionary
	#where the key is the repo package name (repoName) and the value is the ID
	pkgIDs[repoName] = db.insert_id()		

	#CHECK WHAT WAS PUT INTO THE DB, EVENTUALLY NEED TO DO COMMIT
	#db.query("""SELECT name FROM ac_softwareitem""")
	#r=db.store_result()
	#print "verifying that names in ac_softwareitem"
	#for row in r.fetch_row(1000):
	#	print row

#for each repoPkg, get its ID from the database (it has an ID because I inserted it into
#the DB in the loop before this)
#
repoPkgCounter = 0
depCounter = 0
findDepsErrorCounter = 0
depNotInDBCounter = 0
errorInsertingDBCounter = 0

#for repoPkg in pl.installed:	
for repoPkg in sorted(pl.available):
	
	repoPkgCounter = repoPkgCounter+1
	print "repoPkg number ",repoPkgCounter
	pkgs = []
	ematch, match, unmatch = base.pkgSack.matchPackageNames([str(repoPkg)])

	for po in ematch + match:
		pkgs.append(po)
		#get dependencies
		try:
			dependencies = base.findDeps(pkgs)
		except Exception, e:
			print "findDeps had an error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
			findDepsErrorCounter = findDepsErrorCounter + 1
		else:

			#software is the db - already linked to it
			#ac_softwareitem is the table that holds all info about packages
			#ac_softwaredepend has the Id of the software and the ID of what it depends on
			#if it has multiple dependencies it will be listed multiple times
			#i need to insert into relevant fields
			#NOW USE EARLIER CODE TO LOOP THROUGH DEPENDENCIES
	
			d = {}

			for key1, values in dependencies.items():
		
				for key2, values2 in values.items():
				  print "printing values2"
				  print values
				  depCounter = depCounter + 1
				
				  repoName = str(repoPkg.base_package_name)

				  repoVersion = str(repoPkg.version)

				  repoRelease = str(repoPkg.rel)
				  #all of the info needed is in values[0]. Need to verify this

				  #place each package base name, version, and release into dictionary.
				  #The key is base name, value is a tuple with version and release			
				  
				  #try:
				    #do i really need this dictionary
				  d[values2[0].base_package_name] = values2[0].version,values2[0].rel
				  #except Exception, e:
				    #print "Error trying to do d[values2[0].base_package_name]"
				  #else:				  
				
				  #print values2[0].requires_names
				
				  name = values2[0].base_package_name
				  version = values2[0].version
				  release = values2[0].rel					
				 								
				  #search pkgIDs dictionary for this ID
				
				  repoID = pkgIDs[repoName]
				  try:
						depID = pkgIDs[name]
				  except KeyError:
						print "The dependency ",name," for package ",repoName
						print "does not exist in the database"
						depNotInDBCounter = depNotInDBCounter + 1
				  else:
					
						print "repo package name, version, release"
						print repoName, repoVersion, repoRelease
						print "dependency package name, version, release"
						print name,version,release		
						print "repo ID and dep ID"
						print repoID,depID
						try:
						  cursor.execute (""" INSERT INTO ac_softwaredepen(id_software,id_dependen) 							  VALUES (%s,%s) """,(repoID,depID))	
						  print "Inserted into DB"
						except Exception, e: 
						  print "Error inserting into DB"
						  errorInsertingDBCounter = errorInsertingDBCounter + 1
						  print	
						else:						
						  print		
				
print "There were ",repoPkgCounter," repoPackages"
print "There were ",depCounter," dependencies"
print "There were ",findDepsErrorCounter," errors when calling findDeps"
print "There were ",depNotInDBCounter," errors trying to find a dependency in the database (it did not exist)"
print "There were ",errorInsertingDBCounter," errors trying to insert info into the database"
print

#numrows = int(cursor.rowcount)
#print numrows
cursor.execute("SELECT * FROM ac_softwaredepen")
#cursor.execute("SELECT * FROM ac_softwareitem")
results = cursor.fetchall()

#rows = cursor.fetchall()
#for row in rows:
#    print row

