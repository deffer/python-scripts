# Generic function for updating Weblogic system resources
def update_system_resources(clusterName):
   print "Cluster name is " + clusterName
   startTransaction()
        create_JMSSystemResource("/", "DummyJMSModule")
   	delete_JMSModule("/JMSSystemResources", "DummyJMSModule")
   endTransaction()
   print "update_system_resources function has finished"
#***************************************