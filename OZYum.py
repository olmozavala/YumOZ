import sys 
import yum 
import MySQLdb
import pdb

sys.path.append('/usr/share/yum-cli')
from output import *
from yumcommands import *
from cli import *
from datetime import datetime
from DBManager import *


dbObj = DBManager()
base = cli.YumBaseCli()

modTypes = {'insert':'Init','removed':'Removed', 'restored' :'Restored', 'modified' :'Modified'}
textInsert = 'First time insertion of package'
textMod= 'The version or release has being modified'
textMissDepGroup = 'Unavailable'


def insertDep(pkgs):
    """It searches and inserts the dependencies of all the received pkgs"""

    print "UPDATING ALL THE DEPENDENCIES"

    for pkg in pkgs:
        name = str(pkg.name) #Name of the package
        print "-------Finding dependencies for: "+name

        id = dbObj.idFromPkgName(name)
        if(id == None):
            print "ERROR Finding Dependencies. The current package: " + name + " doesn't exist in the DB"
            break

        temppkgs = [] # Used to store the packages that match the asked name
        ematch, match, unmatch = base.pkgSack.matchPackageNames([name])
        for po in ematch + match:# Merges int temppkgs the packages that match the name
            temppkgs.append(po)

        dependencies = base.findDeps(temppkgs)# Finds the dependecies of the package

        for pkg in dependencies:
            for req in dependencies[pkg]:
                reqlist = dependencies[pkg][req] 
                #print "REQ:",req # This one contains the dependency
                #print "REQLIST",reqlist # This one contains the provider
                
                depname = req[0]

                #pdb.set_trace()
                for po in reqlist:
                    #TODO search for the 'base-name' of the provider
                    # po is the type YumAvailablePackage
                    #print "Provider or dependency name: %s" % po.name
                    depname = po.name # If we have a provider we use that insted of the dependency name

                    print "Dependency name:",depname
                    depid = dbObj.idFromPkgName(depname)

                    if(depid == None):
                        #TODO Put this package in the not available group
                        print "The current dependency was not found:%s"%depname
                    else:
                        dbObj.insertDepen(id[0],depid[0])
                        break #Go to next dependency


def updatePkgs(pkgs):
    """It inserts a list of packages into the database"""
    now = datetime.now()
    str_now = now.date().isoformat()
    
    print "UPDATING THE DATABASE OF PACKAGES"

    count = 1;
    for pkg in pkgs:
        name = str(pkg.name)
        version = str(pkg.version)
        release = str(pkg.release)
        summary = str(pkg.summary)
        desc = str(pkg.description)

        # Obtain all the current 'names' of the packages
        cpkg= dbObj.pkgFromName(name)

        if cpkg==None: #In this case the current package is not in the database so we insert as new package
            print "Inserting package:",name

            ### Inserting the new package into the database 
            dbObj.insertPkg(name, desc,summary, version, release, 1)
            dbObj.commit()

            ### Inserting the inital insertion into the database
            id = dbObj.idFromPkgName(name)
            if(id==None):
                print "BIG ERROR DIDN'T FOUND A PACKAGE THAT WAS JUST STORED"
                break

            dbObj.insertModif( str_now,modTypes['insert'],textInsert,id[0])
            dbObj.commit()

        else:# In this case the package already existed. We verify that the version and release are the same
            cid = cpkg[0]      #id
            cname = cpkg[1]    #name
            cdesc = cpkg[2]
            csum =  cpkg[3]
            #csrpm = cpkg[4]
            cavai = cpkg[5]
            cversion = cpkg[6]
            crelease = cpkg[7]

            # If the version or release is different then we add a modification
            if ( (cversion!=version) or (release!=crelease)):
                print "The package ",cname," has being modified, updating the version"
                print "Version %s -- %s Release %s -- %s"%(version,cversion,release,crelease)
            
                dbObj.updatePkg(cid, version, release, desc, summary)
                dbObj.insertModif(str_now,modTypes['modified'],textMod,cid)
                dbObj.commit()


def GetPkgs(lst, description, outputType, highlight_na={},
                 columns=None, highlight_modes={}):

    print description
    sortPkg =[] 

    for pkg in sorted(lst):
        key = (pkg.name, pkg.arch)
        highlight = False
        if False: pass
        elif key not in highlight_na:
            highlight = highlight_modes.get('not in', 'normal')
        elif pkg.verEQ(highlight_na[key]):
            highlight = highlight_modes.get('=', 'normal')
        elif pkg.verLT(highlight_na[key]):
            highlight = highlight_modes.get('>', 'bold')
        else:
            highlight = highlight_modes.get('<', 'normal')
        sortPkg.append(pkg)

    return sortPkg


def DispPkgs(pkgs):
   for pkg in pkgs:
        print pkg.name + "." + pkg.version + "." +  pkg.release


if __name__=="__main__":

    """Now this is to OZ version, it should get the same result"""
    #extcmds = ['ttf-zh-song']
    extcmds = ['all']
    #extcmds = ['libhugetlbfs']
    basecmd = 'info'
    try:
        highlight = base.term.MODE['bold']
        ypl = base.returnPkgLists(extcmds, installed_available=highlight)
    except yum.Errors.YumBaseError, e:
        print [str(e)]
    else:#This happends if no ecxeption occured
        update_pkgs = {}
        inst_pkgs   = {}
        local_pkgs  = {}

        columns = None

        if highlight and ypl.installed:
            #  If we have installed and available lists, then do the
            # highlighting for the installed packages so you can see what's
            # available to update, an extra, or newer than what we have.
            for pkg in (ypl.hidden_available +
                        ypl.reinstall_available +
                        ypl.old_available):
                key = (pkg.name, pkg.arch)
                if key not in update_pkgs or pkg.verGT(update_pkgs[key]):
                    update_pkgs[key] = pkg

        if highlight and ypl.available:
            #  If we have installed and available lists, then do the
            # highlighting for the available packages so you can see what's
            # available to install vs. update vs. old.
            for pkg in ypl.hidden_installed:
                key = (pkg.name, pkg.arch)
                if key not in inst_pkgs or pkg.verGT(inst_pkgs[key]):
                    inst_pkgs[key] = pkg

        if highlight and ypl.updates:
            # Do the local/remote split we get in "yum updates"
            for po in sorted(ypl.updates):
                if po.repo.id != 'installed' and po.verifyLocalPkg():
                    local_pkgs[(po.name, po.arch)] = po

        # Output the packages:
        clio = base.conf.color_list_installed_older
        clin = base.conf.color_list_installed_newer
        clir = base.conf.color_list_installed_reinstall
        clie = base.conf.color_list_installed_extra
        rip = GetPkgs(ypl.installed, '---------------Installed Packages', basecmd,
                            highlight_na=update_pkgs, columns=columns,
                            highlight_modes={'>' : clio, '<' : clin,
                                             '=' : clir, 'not in' : clie})
        #DispPkgs(rip)
        
        clau = base.conf.color_list_available_upgrade
        clad = base.conf.color_list_available_downgrade
        clar = base.conf.color_list_available_reinstall
        clai = base.conf.color_list_available_install
        rap = GetPkgs(ypl.available, '---------------Available Packages', basecmd,
                            highlight_na=inst_pkgs, columns=columns,
                            highlight_modes={'<' : clau, '>' : clad,
                                             '=' : clar, 'not in' : clai})
        #DispPkgs(rap)
              
        rep = GetPkgs(ypl.extras, '---------------Extra Packages', basecmd,
                            columns=columns)

        #DispPkgs(rep)

        cul = base.conf.color_update_local
        cur = base.conf.color_update_remote
        rup = GetPkgs(ypl.updates, '---------------Updated Packages', basecmd,
                            highlight_na=local_pkgs, columns=columns,
                            highlight_modes={'=' : cul, 'not in' : cur})
        #DispPkgs(rup)

        rrap = GetPkgs(ypl.recent, '---------------Recently Added Packages',
                             basecmd, columns=columns)

        if(len(sys.argv) == 1):
            print "Updating available packages info"
            updatePkgs(rap)
            #insertDep(rap)#Insert the dependencies of all the new packages
        else:
            if( sys.argv[1] == "populate"):
                print "Initial populate of the DB first from installed packages and then with available packages"
                dbObj.clearAllTables()
                updatePkgs(rip)
                updatePkgs(rap)

                insertDep(rip)#Insert the dependencies of all the installed packages
                insertDep(rap)#Insert the dependencies of all the new packages
