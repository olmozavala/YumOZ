import yum
import os
import sys
#import yumcommands
#import sys
#sys.path.append('yumcommands')


#instantiate YumBase object so finddeps can be accessed
base = yum.YumBase()

#I don't remember why this needs to be here, I am commenting it out for now to see 
#if the code still runs
#base._getTs(False)

#convert what would be a normal command line argument specifying a package
#into a package object, so it can be passed into findDeps
pkgs = []
ematch, match, unmatch = base.pkgSack.matchPackageNames(['httpd'])
for po in ematch + match:
    pkgs.append(po)

#get dependencies
dependencies = base.findDeps(pkgs)

print
print "There are "+repr(len(dependencies))+" dictionaries of dictionaries"

#indexes for looping through dict of dicts
dictNum1=-1
dictNum2=-1

#create dictionary of base names, values are tuples of release and version
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
		#print values2[0].base_package_name
		#print values2[0].version
		#print values2[0].rel
		d[values2[0].base_package_name] = values2[0].version,values2[0].rel
		#print values2[0].requires_names

for key, value in d.items():
	print key,value

#print dependencies['YumAvailablePackageSqlite']

#get list of packages from repositories
base.conf.cache = os.geteuid() != 1
pl = base.doPackageLists(patterns=sys.argv[1:])
if pl.installed:
    print "pl.installed"
    for pkg in sorted(pl.installed):
        print pkg
if pl.available:
    print "pl.available"
    for pkg in sorted(pl.available):
        print pkg, pkg.repo
if pl.reinstall_available:
    print "pl.reinstall_available"
    for pkg in sorted(pl.reinstall_available):
        print pkg, pkg.repo

#insert into DB
#get description and summary
#learn pythin with the sql stuff
#yum code might have summary/description
#yum info httpd - look at yum code info command - should have summ/descri


