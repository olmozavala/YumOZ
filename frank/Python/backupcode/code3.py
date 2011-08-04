import yum
import os
import sys
#import _mysql
import MySQLdb
#import yumcommands
#import sys
#sys.path.append('yumcommands')


#instantiate YumBase object so finddeps can be accessed
base = yum.YumBase()

#establish database connection
db=MySQLdb.connect(host="localhost",db="software")
cursor=db.cursor()

#get list of packages from repositories
base.conf.cache = os.geteuid() != 1
pl = base.doPackageLists(patterns=sys.argv[1:])
#if pl.installed:
#    print "pl.installed"
#    for pkg in sorted(pl.installed):
#        print pkg
#if pl.available:
#    print "pl.available"
    #for pkg in sorted(pl.available):
        #print pkg, pkg.repo
#if pl.reinstall_available:
#    print "pl.reinstall_available"
    #for pkg in sorted(pl.reinstall_available):
        #print pkg, pkg.repo

#loop over each installed package from repo
#for each one, find dependencies and insert into database
#THIS IS ONLY DONE FOR pl.installed right now!

for repoPkg in sorted(pl.installed):
	repoName = str(repoPkg.base_package_name)
	repoVersion = str(repoPkg.version)
	repoRelease = str(repoPkg.rel)
	print "inserting repopkg name, version, release into database"
	print repoName, repoVersion, repoRelease
	#sql = "INSERT INTO ac_softwareitem(name,version,release) VALUES ('%s','%s','%s')" , \
	#(repoName, repoVersion, repoRelease)
	#cursor.execute(sql)

	#WHY CANT I GET THE RELEASE IN?

	cursor.execute (""" INSERT INTO ac_softwareitem (name,version) VALUES (%s,%s) """,
			(repoName,repoVersion))
	

	#CHECK WHAT WAS PUT INTO THE DB, EVENTUALLY NEED TO DO COMMIT
	#db.query("""SELECT name FROM ac_softwareitem""")
	#r=db.store_result()
	#print "verifying that names in ac_softwareitem"
	#for row in r.fetch_row(1000):
	#	print row
	
	pkgs = []
	ematch, match, unmatch = base.pkgSack.matchPackageNames([str(repoPkg)])
	for po in ematch + match:
    		pkgs.append(po)
		#get dependencies
		dependencies = base.findDeps(pkgs)
		#software is the db - already linked to it
		#ac_softwareitem is the table that holds all info about packages
		#ac_softwaredepend has the Id of the software and the ID of what it depends on
		#if it has multiple dependencies it will be listed multiple times
		#i need to insert into relevant fields
		#NOW USE EARLIER CODE TO LOOP THROUGH DEPENDENCIES
		
		d = {}

		#loop through dictionary of dictionaries to see what it contains. 

		for key1, values in dependencies.items():
			#print
			#dictNum1=dictNum1+1
			for key2, values2 in values.items():
				#print "Currently in key # "+repr(dictNum1)+". It is "+repr(key1)
				#dictNum2=dictNum2+1
				#print "Displaying sub-key # "+repr(dictNum2)+". It is "+repr(key2)
				#print "The key's type is "+repr(type(key2))
				#print "Its value is "+repr(values2)
				#l=values2
				#print "The value's type is "+repr(type(values2))		
				#print

				#place each package base name, version, and release into dictionary.
				#The key is base name, value is a tuple with version and release
				
				d[values2[0].base_package_name] = values2[0].version,values2[0].rel
				#print values2[0].requires_names
				name = values2[0].base_package_name
				version = values2[0].version
				release = values2[0].rel
				cursor.execute (""" INSERT INTO ac_softwareitem (name,version) VALUES (%s,%s) """\
				,(name,version))

				#cursor.execute(sql)














#I don't remember why this needs to be here, I am commenting it out for now to see 
#if the code still runs
#base._getTs(False)



#convert what would be a normal command line argument specifying a package
#into a package object, so it can be passed into findDeps


#pkgs = []
#ematch, match, unmatch = base.pkgSack.matchPackageNames(['httpd'])
#for po in ematch + match:
#    pkgs.append(po)

#get dependencies
#dependencies = base.findDeps(pkgs)

#print
#print "There are "+repr(len(dependencies))+" dictionaries of dictionaries"

#indexes for looping through dict of dicts
#dictNum1=-1
#dictNum2=-1

#create dictionary of base names, values are tuples of release and version
#d = {}

#loop through dictionary of dictionaries to see what it contains. 

#for key1, values in dependencies.items():
	#print
	#dictNum1=dictNum1+1
#	for key2, values2 in values.items():
		#print "Currently in key # "+repr(dictNum1)+". It is "+repr(key1)
		#dictNum2=dictNum2+1
		#print "Displaying sub-key # "+repr(dictNum2)+". It is "+repr(key2)
		#print "The key's type is "+repr(type(key2))
		#print "Its value is "+repr(values2)
		#l=values2
		#print "The value's type is "+repr(type(values2))		
		#print

		#place each package base name, version, and release into dictionary.
		#The key is base name, value is a tuple with version and release
		#print values2[0].base_package_name
		#print values2[0].version
		#print values2[0].rel
#		d[values2[0].base_package_name] = values2[0].version,values2[0].rel
		#print values2[0].requires_names


#for key, value in d.items():
#	print key,value


#print dependencies['YumAvailablePackageSqlite']



#insert into DB
#get description and summary
#learn pythin with the sql stuff
#yum code might have summary/description
#yum info httpd - look at yum code info command - should have summ/descri

#DB stuff#conn = MySQLdb.connect (host = "local", user = "Bre(nt", passwd = "brentw", db="software")
#db=_mysql.connect(host="localhost",user="Brent",passwd="brentw",db="software")
#db=MySQLdb.connection(host="localhost",db="software")
#db.query("""SELECT version FROM ac_softwareitem""")
#db.store_result()
#db.fetch_row()
