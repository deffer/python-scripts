from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
from os.path import exists
from shutil import copyfile, copytree, copy
from xml.etree.ElementTree import register_namespace

import sys, os, re

BUILDXML='build.xml'
WEBXML = 'WebContent/WEB-INF/web.xml'

projectname=''
svnrepo='https://subversion.auckland.ac.nz/svn/UoA.ITSS.GrpApps/WebLogicIntegration/NSIStudentSubscriber'

earfolder=''
webfolder=''
utilfolder=''

fail_on_error = 'true'
bamboo_plan_name = 'DUMMY'

DELETE_FROM_ENV=[
   "property[@file='build.properties']",
   "property[@environment='env']",
   "condition[@property='wl.home']",
   "condition[@property='bea.home']",
   "fail[@unless='wl.home']",
   "fail[@unless='bea.home']"   
]


ENV_FROM_ROOT=[
   "property[@environment='env']",
   "condition[@property='wl.home']",
   "condition[@property='bea.home']",
   "fail[@unless='wl.home']",
   "fail[@unless='bea.home']"   
]

def updateBuildXMLEnvironment(tree):
    env_defined = True
    root = tree.getroot()
    for xpath in ENV_FROM_ROOT:
        pdel = root.find(xpath)
        if pdel==None:            
            env_defined = False

    if env_defined:
        print ("WARNING! wl.home and bea.home are defined in the <project> element. There two property file values file will be ignored.")
        
    penv = tree.find("./target[@name='init.env']")

    for xpath in DELETE_FROM_ENV:
        pdel = penv.find(xpath)
        if not pdel==None:            
            print ("...deleting:  {} from init.env".format(pdel.tag))
            penv.remove(pdel)

    print("...updating environment variables")
    penv.append(Element("property",{'environment':"env"}))
    penv.append(Element("property",{'file':"build.properties"}))
        
    el = Element("condition",{'property':"wl.home", 'value':"${env.WL_HOME}"})
    el.append(Element("isset",{'property':"env.WL_HOME"}))
    penv.append(el)
    penv.append(Element("fail",{'unless':"wl.home", 'message':"The WL_HOME environment variable needs to be set! e.g. WL_HOME=c:/bea/weblogic92"}))

    el = Element("condition",{'property':"bea.home", 'value':"${env.BEA_HOME}"})
    el.append(Element("isset",{'property':"env.BEA_HOME"}))
    penv.append(el)
    penv.append(Element("fail",{'unless':"bea.home", 'message':"The BEA_HOME environment needs to be set!, e.g. BEA_HOME=c:/bea"}))

    return True

def updateBuildXMLEnvWeblogicJar(tree):
    penv = tree.find("./target[@name='init.env']")
    if penv.find("./property[@name='weblogic.jar']") is None:
        penv.append(Element("property",{'name':"weblogic.jar", 'value':"${wl.home}/server/lib/weblogic.jar"}))
        print ("...adding property weblogic.jar")
    else:
        print ("...skipping property weblogic.jar as it is already set")
    return True
    
def updateBuildXMLSetDefaultTarget(tree):
    theattr = 'archive'
    p = tree.getroot()    
    attr = p.get('default')    
    if attr!=theattr:
        print("...changing project default target ({}) to {}".format(attr, theattr))
    else:
        print("...no changes to project default target")
    return True

def updateBuildXMLAddArchiveDependsOnBuild(tree):
    p = tree.find("./target[@name='archive']")
    if p==None:
        print ("Target 'archive' is missing")
        return False;

    dependsline = p.get("depends")
    r = dependsline.split(',')
    s = set()
    for w in r:
        s.add(w.strip())
    if 'build' not in s:        
        s.add('build')
        new = ','.join(s)
        print("...adding dependency. New archive dependency is '{}'".format(new))        
        p.set('depends', new)
    else:
        print("...no changes to archive dependency")
        
    return True

def updateBuildXMLAddCopy(tree):
    global projectname
    p = tree.find("./target[@name='archive']")
    if p==None:
        print ("Target 'archive' is missing")
        return False;

    exists = False
    pc = p.findall("./copy[@file='${archive.dir}/${archive.name}']")
    for x in pc:
        if '.location}/EarContent/APP-INF/lib' in (x.get('todir')):
            exists = True
    if not exists:
        p.append(Element('copy', {'file':'${archive.dir}/${archive.name}', 'todir':'${'+projectname+'Ear.location}/EarContent/APP-INF/lib'}))
        print ("...adding copy task to 'archive'")
    else:
        print ("...skipping target 'archive' as it already has a copy task")
    return True

def updateBuildXMLSetProjectName(tree):
    global projectname
    p = tree.getroot()    
    attr = p.get('name')    
    if attr!=None:
        p.set('name', projectname)
        print("...changing project name ({}) to {}".format(attr, projectname))
    else:
        p.set('name', projectname)
        print("...adding project name {}".format(projectname))
        
    return True

def updateBuildXMLAddReleaseXML(tree):
    p = tree.getroot()
    if p.find('./import[@file="release.xml"]') is not None:
        print("...skipping import release.xml as already existing")
    else:
        p.insert(0, Element('import', {'file':'release.xml'}))
        print("...adding import release.xml")        
    return True

def updateBuildXMLManifest(tree):
    stage = tree.find("./target[@name='stage']")
    if stage is None:
        print("Cant find stage target")
        return False
    
    found = None
    index = 0
    for el in list(stage):
        index = index+1
        if el.tag=='for-each-resource-path':
            found = el
            break
        
    if found is not None:
        print("...adding manifest task to the stage")
        manifest = Element('manifest', {'file':'${staging.dir}/META-INF/MANIFEST.MF'})
        manifest.append(Element('attribute', {'name':'Weblogic-Application-Version', 'value':'${deploy.version.number}'}))
        stage.insert(index, manifest)        
    else:
        print("Cant add manifest task to stage - mkdir is missing")
        
    return True

def updateBuildXMLManifestCP(tree):
    p = tree.find(".//taskdef[@name='build-manifests']")
    
    p.set('classpath', '${weblogic.jar}')
    print("...adding classpath to build-manifests")
    return True

def updateBuildXMLjwscClasspath(tree):
    p = tree.find(".//taskdef[@name='jwsc']")
    p.set('classpath', '${weblogic.jar}')
    print("...adding classpath to jwsc")
    return True

def updateBuildXMLOutputName(tree):
    p = tree.find(".//target[@name='init']/property[@name='archive.name']")
    p.set('value', '${app.name}.ear')
    print("...changing ear file name")
    return True

def updateBuildXMLComponentsXml(tree):
    global projectname
    # find <if><available file="${process.componentbeans.output.dir}"/><then>
    #   or <if><available file="${process.projectbeans.output.dir}"/><then>
    # insert <echo message="****************copy ${VoyagerIDCardSubscriberEar.location}/${process.projectbeans.name}/META-INF/weblogic-ejb-jar.xml to ${ear.staging.dir}/${process.projectbeans.name}/META-INF/weblogic-ejb-jar.xml"/>
    # insert <copy file="${VoyagerIDCardSubscriberEar.location}/${process.projectbeans.name}/META-INF/weblogic-ejb-jar.xml" tofile="${ear.staging.dir}/${process.projectbeans.name}/META-INF/weblogic-ejb-jar.xml" overwrite="true"/>                                                                                                                

    beantypes = ['component','project']
    for x in beantypes:
        t = tree.find("./target[@name='stage.to.ear']")        
        th = t.findall("./if/then")

        name = "${process."+x+"beans.name}"
        locfrom = "${"+projectname+"Ear.location}/"+name+"/META-INF/weblogic-ejb-jar.xml"
        locto = "${ear.staging.dir}/"+name+"/META-INF/weblogic-ejb-jar.xml"
        t.insert(0, Element('mkdir', {'dir':"${"+projectname+"Ear.location}/"+name+"/META-INF/"}))
        
        for ifthen in th:
            #print("i - "+str(len(list(ifthen))))
            if ifthen.find("./copy[@todir='${ear.staging.dir}/"+name+"']") is not None:
                print ("...adding <copy> weblogic-ejb-jar.xml to {}".format(name))
                ifthen.append(Element('echo', {'message': "****************copy {} to {}".format(locfrom, locto)}))
                ifthen.append(Element('copy', {'file':locfrom, 'tofile':locto, 'overwrite':'true', 'failonerror':fail_on_error}))
        
    return True

def updateWebXMLcheckTimeout(foldername):
    webxmlfile = os.path.join(foldername, WEBXML)
    if not exists(webxmlfile):
        print ("File does not exist: "+webxmlfile)
        return False

    print('------>Opening {}'.format(webxmlfile))
    tree = ElementTree()
    tree.parse(webxmlfile)
    fixParsedXML(tree)
    
    found = False
    
    for el in tree.getroot().findall("./env-entry/env-entry-name"):        
        if (el.text is not None) and (el.text.strip() =='serviceTimeout'):
            found = True
            break
    if found:
        print("...web.xml already contains serviceTimeout property")
        return True

    print("... adding serviceTimeout to web.xml")    
    
    el = tree.getroot()
    envEntry = Element('env-entry')

    descr = Element('description')
    descr.text = 'timeout for calling web services'    
    ename = Element('env-entry-name')
    ename.text = 'serviceTimeout'
    etype = Element('env-entry-type')
    etype.text = 'java.lang.Integer'
    evalue = Element('env-entry-value')
    evalue.text = '60000'

    envEntry.append(descr)
    envEntry.append(ename)
    envEntry.append(etype)
    envEntry.append(evalue)
    el.append(envEntry)    

    write_as_is(tree,webxmlfile, xml=True)    
    return True    

def fixParsedXML(tree):
    for el in tree.getroot().iter():
        if el.tag[0] == '{':
            el.tag = el.tag.split('}', 1)[1]
            #print(el.tag)

    el = tree.getroot()
    elid = el.get("id")
    elver = el.get("version")
    for k in el.keys():
        el.set(k, None)
    el.set('id', elid)
    el.set('version', elver)
    el.set('xmlns', 'http://java.sun.com/xml/ns/j2ee')
    el.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    el.set('xsi:schemaLocation','http://java.sun.com/xml/ns/j2ee http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd')

def preprocessBuildXML(foldername):
    filename = os.path.join(foldername, BUILDXML)
    original = os.path.join(foldername, "original.build.xml");
    
    if not exists(original):
        copyfile(filename, original)

    print('------>Opening {}'.format(filename))
    tree = ElementTree()
    tree.parse(original)
    
    return tree                 

def postprocessBuildXML(tree, foldername):
    write_as_is(tree, os.path.join(foldername,"build.xml"))

def checkProjectFolders():
    global projectname, webfolder, earfolder, utilfolder
    earfolder = projectname+"Ear"
    if not exists(earfolder):
        print("Cannot locate Ear folder. Expected {} is not found".format(earfolder))
        return False
    webfolder = projectname+"Web"
    if not exists(webfolder):
        print("Cannot locate Web folder. Expected {} is not found".format(webfolder))
        return False
    utilfolder = projectname+"Utility"
    if not exists(utilfolder):
        utilfolder = projectname+"Util"
        if not exists(utilfolder):
            print("Cannot locate Utility folder. Expected {} or {} are not found".format(projectname+"Utility", utilfolder))
            return False
        
    return True

def write_as_is(tree, filename, xml=False):
    #assuming root is <project>
    print ("...writing file {}...".format(filename))
    f = open(filename, 'w')
    if (xml):
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    write_tag(tree.getroot(), f, 0)
    f.close()
    print ("DONE!")

ATTR_SORTKEYS = {'name':'aa01', 'id':'aa02', 'target':'aa03', 'version':'aa04', 'unless':'aa05','description':'zz9'}
def attrkey(sstr):
    return ATTR_SORTKEYS.get(sstr) if (ATTR_SORTKEYS.get(sstr) is not None) else sstr.lower()

def write_tag(tag, out, indent):
    line = '<'+tag.tag;

    attriterate = sorted(tag.keys(), key = attrkey)
    for key in attriterate:
        val = tag.get(key)
        if val is not None:
            line = line+' {}="{}"'.format(key, val.replace('"', "'"))

    children = list(tag)
    body = tag.text.strip() if tag.text else '';
    
    if len(children)==0 and body == '':
        #close tag and return
        line = line+"/>\n"
        write_line(line, out, indent)
        return

    # new line for those
    if (tag.tag in ['target', 'taskdef', 'for']):
        out.write('\n')

    #if no attributes and single-line body - write on one line
    if len(tag.keys())==0 and len(children)==0 and ('\n' not in body) :
        line= "{}>{}</{}>".format(line, body, tag.tag)
        write_line(line+"\n", out, indent)
        return
        
    #write opening tag
    line = line + ">\n"
    write_line(line, out, indent)

    #write body
    if (body != ''):        
        write_line(body+"\n", out, indent)
    
    #write children
    for p in children:
        write_tag(p, out, indent+1)

    #write closing tag
    line = "</{}>".format(tag.tag)
    write_line(line+"\n", out, indent)

def write_line(line, out, indent):
    '''w = ' '*indent*2+line'''
    w = ''.ljust(indent*2, ' ')+line    
    out.write(w)


def copy_log4j(foldername):
    filename = os.path.join(foldername, "log4j.xml")

    copy_from_template(filename, "configs/log4j.xml.tmpl")   
    '''ft = open("configs/log4j.xml.tmpl", 'r')
    fp = open(filename, 'w')

    str1 = ft.read()
    ft.close()

    str2 = replace_vars(str1)

    fp.write(str2);
    fp.close'''

def copyPropertyFile(foldername):
    filename = os.path.join(foldername, "build.properties")
    
    if exists(filename) and not exists(os.path.join(foldername,"old.build.properties")):
        copyfile(filename, os.path.join(foldername,"old.build.properties"))

    copy_from_template(filename, "configs/build.properties.tmpl")    
    '''ft = open("configs/build.properties.tmpl", 'r')
    fp = open(filename, 'w')

    str1 = ft.read()
    ft.close()

    str2 = replace_vars(str1)

    fp.write(str2);
    fp.close'''

def copy_beans_weblogic_ejb_jar_xml():
    global earfolder, webfolder
    filename = "weblogic-ejb-jar.xml"
    compb = "_WLI_ComponentBeans"
    projb = "_WLI_ProjectBeans"

    for x in [compb, projb]:
        folder = os.path.join(earfolder, webfolder+x, "META-INF")
        targetfile = os.path.join(folder, filename)
        if not exists(targetfile):
            #create folders if neccessary
            if not os.path.isdir(folder):
                os.makedirs(folder)
            #writefile
            copy_from_template(targetfile, os.path.join("configs", x, filename+".tmpl"))

def copy_from_template(filename, templatename):
    ft = open(templatename, 'r')
    fp = open(filename, 'w')

    str1 = ft.read()
    ft.close()

    str2 = replace_vars(str1)

    fp.write(str2);
    fp.close

def replace_vars(text):
    global projectname, utilfolder, bamboo_plan_name
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    replace_map = {
        '%app%':projectname,
        '%util%':utilfolder,
        '%wsdir%':os.getcwd().replace('\\', '/'),
        '%repo%': svnrepo,
        '%bmbwdir%' : bamboo_plan_name
    }
    rc = re.compile('|'.join(map(re.escape, replace_map)))
    def translate(match):
        return replace_map[match.group(0)]
    return rc.sub(translate, text)

def copy_jars(folder):
    names = os.listdir('configs/ear/')
    for file in names:
        srcname = os.path.join('configs/ear/', file)
        if not os.path.isdir(srcname):
            copy(srcname, folder)

    libfolder = os.path.join(folder, 'lib')
    if not os.path.isdir(libfolder):
        os.makedirs(libfolder)
    names = os.listdir('configs/ear/lib')
    for file in names:
        copy(os.path.join('configs/ear/lib', file), libfolder)

TASKS_EAR=[
    updateBuildXMLEnvironment,
    updateBuildXMLEnvWeblogicJar,
    updateBuildXMLSetProjectName,
    updateBuildXMLAddReleaseXML,
    updateBuildXMLManifestCP,
    updateBuildXMLManifest,
    updateBuildXMLAddArchiveDependsOnBuild,
    updateBuildXMLOutputName]

TASKS_WEB=[
    updateBuildXMLEnvironment,
    updateBuildXMLSetProjectName,
    updateBuildXMLComponentsXml,
    updateBuildXMLEnvWeblogicJar,
    updateBuildXMLManifestCP,
    updateBuildXMLjwscClasspath    
    ]

TASKS_UTIL=[
    updateBuildXMLEnvironment,
    updateBuildXMLSetDefaultTarget,    
    updateBuildXMLAddArchiveDependsOnBuild,
    updateBuildXMLAddCopy]

def main():
    global projectname, webfolder, svnrepo, fail_on_error, bamboo_plan_name   

    
    # ######################
    # check arguments
    # ######################
    if len(sys.argv)<2:
        projectname="VoyagerEnrolmentSubscriber"
        svnrepo = "https://subversion.auckland.ac.nz/svn/UoA.ITSS.GrpApps/WebLogicIntegration/VoyagerEnrolmentSubscriber"
        fail_on_error = "false"
        bamboo_plan_name = "VGRENRL" #projectname[0:5].upper()
        #print("1 argument is required: project name (ex. EPRAFASubscriber)")        
        #sys.exit()
    else:
        projectname=sys.argv[1]
        if len(sys.argv)>2:
            svnrepo = sysargv[2]

    # ######################
    # check Ear, Web, Util
    # ######################        
    if not checkProjectFolders():
        sys.exit()

    for (folder, tasks) in {earfolder:TASKS_EAR, webfolder:TASKS_WEB, utilfolder:TASKS_UTIL}.items():    
        # ######################
        # open as XML
        # ######################        
        tree = preprocessBuildXML(folder)
        if not tree:
            sys.exit()

        # ######################
        # Execute functions
        # ######################
        for func in tasks:
            if not func(tree):
                sys.exit()
        postprocessBuildXML(tree, folder)

        # ######################
        # Copy property file
        # ######################
        copyPropertyFile(folder)
        copyfile("workspace.xml", os.path.join(folder,"workspace.xml"))

    # create folders in the Ear project
    deployconfig = os.path.join(earfolder,"configurations","deploy")
    if not os.path.isdir(deployconfig):
        os.makedirs(deployconfig)
    copy_log4j(deployconfig)
    copy_jars(earfolder)
    copy_beans_weblogic_ejb_jar_xml()

    # update web.xml in Web folder
    updateWebXMLcheckTimeout(webfolder)
    # copy handlers jar to Web folder
    copy('configs/web/wli_exception_handling-1.0.jar', os.path.join(webfolder, "WebContent", "WEB-INF", "lib"))

if __name__ == '__main__':
    main()
