import sys, os, re

RE_FIELD = "\s*private\s+static\s+int\s+serviceTimeout\s*;\s*"
RE_GETTER = "\s*public\s+static\s+int\s+getServiceTimeout\s*\(\s*\)"
RE_INIT="\s*public\s+void\s+contextInitialized\s*\(\s*ServletContextEvent\s+[^\)]+\s*\).*"
RE_FUNCDEF = "\s*(public|private)\s+.+\(.*\).+"


ADD_FIELD = "\tprivate static int serviceTimeout;"
ADD_GETTER = "\tpublic static int getServiceTimeout() {\n\t\treturn serviceTimeout;\n\t}	"
# val.replace('@1', appname)
ADD_LOOKUP = '''    private void lookupTimeout(){\n
    try{
        InitialContext ic= new InitialContext();
        tserviceTimeout = (Integer)ic.lookup("java:/comp/env/serviceTimeout");
    }catch(NamingException e){
        Logger logger = Logger.getLogger("@1");
        logger.error("Environment variable serviceTimeout is not configured");
    }\n'''


re_nonempty = re.compile("(\s*)(//[^/]*\)(s*)")

def test():
    rc = re.compile(RE_FIELD)
    s = "	private static int serviceTimeout ;	"
    if not rc.match(s):
        print("RE_FIELD does not match test string")
        return False

    rc = re.compile(RE_INIT)
    s = "	public void contextInitialized(ServletContextEvent sce) {"
    if not rc.match(s):
        print("RE_INIT does not match test string")
        return False
    
    rc = re.compile(RE_GETTER)
    s = "	public static int getServiceTimeout() {"
    if not rc.match(s):
        print("RE_GETTER does not match test string")
        return False

    rc = re.compile(RE_FUNCDEF)
    for s in ["   private void lookUpServiceControlEndPoints() {",
              "	public static String getAfaServiceControlEndPoint() {",
              "	public void contextDestroyed(ServletContextEvent arg0) {",
              "	private void setupLog4jProperties (){"]:
        if not rc.match(s):
            print("RE_FUNCDEF does not match test string --> "+s)
            return False    

appname = "EPRAFAIntegration"

def processTimeout(filename):
    global appname
    lines = open(filename,'r').readlines()

    for regxp in [RE_FIELD, RE_GETTER]:
        rc = re.compile(regxp)
        fred = find(lambda string: rc.match(string), lines)
        if fred:
            print("FOUND --> "+fred)
            return True

    # insert field
    rc = re.compile(RE_INIT)
    init_func_def_line = find(lambda string: rc.match(string), lines)
    if not init_func_def_line:
        print("Unable to find contextInitialized() function")
        return False
    init_func_def_index = lines.index(init_func_def_line)
    insert_index = searchNonEmptyUp(lines, init_func_def_index)
    if not insert_index:
        print("Unable to find fields definition")

    insert_line = ADD_FIELD
    lines.insert(insert, init_func_def_index)

    
    

def searchNonEmptyUp(lines, indexfrom):
    if (indexfrom<=0):
        return False

    print("...looking UP...")
    for i in range(indexfrom-1,0):
        s = lines[i]
        if re_nonempty.match(s):
            print("Found --> "+s)
            return i
    return False

def main():
    global appname
    appname = "EPRAFAIntegration"
    return

if __name__ == '__main__':
    if not test():        
        exit
    main()
