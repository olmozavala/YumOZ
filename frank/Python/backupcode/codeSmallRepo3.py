import yum
import os
import sys
import MySQLdb
import re

#instantiate YumBase object so finddeps can be accessed

base = yum.YumBase()

#establish database connection

db=MySQLdb.connect(host="localhost",db="software")

cursor=db.cursor()

#get list of packages from repositories

base.conf.cache = os.geteuid() != 1

#pl = base.doPackageLists(pkgnarrow='all', showdups=True)
#pl = base.pkgSack.returnPackages(repoid='test-repo', patterns=None, ignore_case=False)
pl = base.pkgSack.returnPackages(patterns=None, ignore_case=False)
#print pl
print""

#merge pl.installed and pl.available 

#pl.installed.append(pl.available)

repoPkgsDict = {}

counter = 0
#put them in a dictionary - remove duplicates
for pkg in pl:
	counter = counter+1
 	repoPkgsDict[counter] = pkg

allRepoPkgs = repoPkgsDict.values()

#print counter
#x = raw_input("Press Enter")

#loop over each installed package from repo.
#for each one, find dependencies and insert into database.

pkgIDs = {}

print "*******************************************************"
print "Inserting all repo packages into the database"
print ""
for repoPkg in allRepoPkgs:
#for repoPkg in sorted(pl.available):

  try:
        repoName = str(repoPkg.base_package_name)

        repoVersion = str(repoPkg.version)

        repoRelease = str(repoPkg.rel)

  except Exception, e:
    print "Error trying to get repoPkg name, version, or release!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  else:
	#print "inserting repopkg name, version, release into database"
	print "name, version, release"

	print repoName, repoVersion, repoRelease

	# check to see if this name, version, release exists already in the database.
	# if it doesn't, insert it to get auto-incremented ID. if it does, get its
	# ID and put it into pkgIDs dictionary.	
	
	#add release to this!!!

	#num will have the number of matches. 
	num=cursor.execute(""" SELECT id FROM ac_softwareitem WHERE name = (%s) AND version = (%s) """,(repoName,repoVersion));
	#num=cursor.execute(""" SELECT id FROM ac_softwareitem WHERE name = (%s) AND version = (%s) """,(repoName,repoVersion));	
	#get the matched ID number
	thisMatch=cursor.fetchall()
	
	
	if num >= 1:		
		thisTuple = thisMatch[0]
		thisID = thisTuple[0]
		pkgIDs[repoName] = thisID
		print "Match found in the DB!"
		print "using "+str(thisID)+" as ID number"
		print ""
		if num > 1:
			print repoName+" "+repoVersion+" existed in multiple places in the DB."
			print "The code will use the ID at the first location found"	
			print ""
	else:
		print "No matches found in the DB. Inserting this into the DB to get an ID number "
	
		#WHY CANT I GET THE RELEASE IN? JUST DO NAME AND VERSION RIGHT NOW
	
		try:	
			cursor.execute (""" INSERT INTO ac_softwareitem (name,version,`release`) VALUES (%s,%s,%s) """,
				(repoName,repoVersion,repoRelease))
			#cursor.execute (""" INSERT INTO ac_softwareitem (name,version) VALUES (%s,%s) """,
				#(repoName,repoVersion))
		except Exception, e:
				#print repoName+","+" repoVersion ",+"already found in DB"
				print "error inserting into ac_softwareitem!!!!!"
				print ''
				print e
				print ""
				db.rollback()			
				sys.exit()
		else:	

			#this will now have an auto-incremented ID. Get it and store it in a dictionary
			#where the key is the repo package name (repoName) and the value is the ID
			pkgIDs[repoName] = db.insert_id()	
			print "ID is "+ str(pkgIDs[repoName])	

db.commit()
print "Database insertions done"
print "*******************************************************"


#for each repoPkg, get its ID from the database (it has an ID because I inserted it into
#the DB in the loop before this)
#
repoPkgCounter = 0
depCounter = 0
findDepsErrorCounter = 0
depNotInDBCounter = 0
errorInsertingDBCounter = 0
depNotHereCounter = 0

print ""
print "*******************************************************"
print "Finding dependencies for each repo package"
print ""
#for repoPkg in pl.installed:	
for repoPkg in allRepoPkgs:
	
	repoPkgCounter = repoPkgCounter+1
	print "repoPkg number",repoPkgCounter, "is named",repoPkg.base_package_name
	print ""
	pkgs = []
	ematch, match, unmatch = base.pkgSack.matchPackageNames([str(repoPkg)])

	for po in ematch + match:		
		print ""
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

			for key1, values1 in dependencies.items():
		
				for key2, values2 in values1.items():
				  #print ""
				  #print "printing values2"
				  #print ""
				  #print values2
				  #print ""
				  #print "printing key2"
				  #print key2
				  #print
				  depCounter = depCounter + 1
				
				  repoName = str(repoPkg.base_package_name)

				  repoVersion = str(repoPkg.version)

				  repoRelease = str(repoPkg.rel)
				  #all of the info needed is in values[0]. Need to verify this

				  #place each package base name, version, and release into dictionary.
				  #The key is base name, value is a tuple with version and release			
				  
				  try:
				    #do i really need this dictionary
				    d[values2[0].base_package_name] = values2[0].version,values2[0].rel
				  except Exception, e:
				    print "package "+str(repoPkg.base_package_name)+" has a dependency "+key2[0]+" that " 				    	    +"isn't here"
				    depNotHereCounter = depNotHereCounter + 1
				    print ""
				  else:				  
				
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
			
						print "Dependency found!"
																
						print "repo package name, version, release"
						print repoName, repoVersion, repoRelease
						print "dependency package name, version, release"
						print name,version,release		
						print "repo ID and dep ID"
						print repoID,depID
						try:
						  cursor.execute (""" INSERT INTO ac_softwaredepen(id_software,id_dependen) 							  VALUES (%s,%s) """,(repoID,depID))	
						  db.commit()
						  print "Inserted into DB"
						except MySQLdb.IntegrityError:
						  print "This is correlation is already in the DB - skipping!"
						  db.rollback()	
						  print ""
						except Exception, e: 
						  print "Error inserting into DB"
						  errorInsertingDBCounter = errorInsertingDBCounter + 1
						  print e
						  print	
						  db.rollback()
						else:						
						  print		
print "Dependency finding is done"
print "*******************************************************"	
print ""	
print "There were ",repoPkgCounter," repoPackages"
print "There were ",depCounter," dependencies"
print "There were ",findDepsErrorCounter," errors when calling findDeps"
print "There were ",depNotInDBCounter," errors trying to find a dependency in the database (it did not exist)"
print "There were ",errorInsertingDBCounter," errors trying to insert info into the database (a duplicate entry is not considered an error)"
print "There were ",depNotHereCounter," errors involving a dependency not here"
print

#numrows = int(cursor.rowcount)
#print numrows
#cursor.execute("SELECT * FROM ac_softwaredepen")
#results = cursor.fetchall()
#cursor.execute("SELECT * FROM ac_softwareitem")
#results = cursor.fetchall()

#rows = cursor.fetchall()
#for row in rows:
#    print row
#db.commit()