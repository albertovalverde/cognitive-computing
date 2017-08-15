#
# Tired of 'Service "ALChoregraphe" (#2344) is already registered.' ?
# ME TOO !!!
#
# Let's do some cleaning :)
# 

# v0.7; get service id from nammed attribute

import sys

def remove_choregraphe_service( robot_ip ):
    session = qi.Session()
    session.connect("tcp://%s:9559" % (robot_ip))

    services = session.services()
    for s in services :
        #print( "s: %s" % s );
        strName = s["name"];
        try:
            serviceID = s["serviceId"];
        except: 
            serviceID = s[1]
        if strName in ["ALChoregraphe", "ALChoregrapheRecorder"] :
            session.unregisterService( serviceID )
            print "%s unregistered !" % serviceID

if __name__ == "__main__" :

	try :
		import qi
	except :
		print "PyNaoqi required ! :("
		exit()

	if len(sys.argv) < 2 :
		print "Usage : %s <robot ip>" % sys.argv[0]
		exit()

	remove_choregraphe_service( sys.argv[1] )
