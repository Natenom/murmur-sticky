#!/usr/bin/env python
# -*- coding: utf-8
#
# sticky.py - Puts a user into a STicky channel; works even after reconnect. (With temporary groups).
#
# Copyright (c) 2010, Natenom / Natenom@googlemail.com
# Version: 0.1.0
# 2010-09-09

## Server settings ##
iceslice='/usr/share/slice/Murmur.ice'
serverport=64738
iceport=60000
icesecret="secureme"
serverid=1

## Sticky Settings ##
st_channel=1349 #Id of the sticky channel.
st_group="stilletreppekinder" #Name of the group for sticky users.

## Messages ##
msg_addstatus="ST setzen..."
msg_removestatus="ST entfernen..."
msg_STremoved="<font style='color:green;font-weight:bold;'>Der Benutzer \"%s\" wurde durch \"%s\" rehabilitiert.</font>"
msg_STadded="<font style='color:red;font-weight:bold;'>Der Benutzer \"%s\" hat einen STicky durch \"%s\" bekommen; Besuche sind erlaubt.</font>"
msg_stillST="<font style='color:red;font-weight:bold;'>You are still on STicky status.</font>"
## DO NOT EDIT BELOW THIS LINE ##

st_user={} #Termporary list of sticky UserIDs

import Ice, sys
Ice.loadSlice("--all -I/usr/share/slice %s" % iceslice)

import Murmur

class MetaCallbackI(Murmur.MetaCallback):
    def started(self, s, current=None):
        serverR=Murmur.ServerCallbackPrx.uncheckedCast(adapter.addWithUUID(ServerCallbackI(server, current.adapter)))
        server.addCallback(serverR)

    def stopped(self, s, current=None):
        return 0

class ServerCallbackI(Murmur.ServerCallback):
    def __init__(self, server, adapter):
      self.server = server
      self.contextR=Murmur.ServerContextCallbackPrx.uncheckedCast(adapter.addWithUUID(ServerContextCallbackI(server)))

    def userConnected(self, p, current=None):
        global st_user, st_group
	if (self.server.hasPermission(p.session, 0, Murmur.PermissionWrite)): #Only admins in root channel can use ST.
	    self.server.addContextCallback(p.session, "stadd", msg_addstatus, self.contextR, Murmur.ContextUser)
	    self.server.addContextCallback(p.session, "stdel", msg_removestatus, self.contextR, Murmur.ContextUser)
	
	UserState=self.server.getState(p.session)
	
	if (UserState.userid in st_user):
	    self.server.addUserToGroup(0, p.session, st_group) #Add user to server group.
	    UserState.channel=st_channel
	    self.server.setState(UserState) #Move him to ST channel
	    self.server.sendMessage(UserState.session, msg_stillST)

    def userDisconnected(self, p, current=None):
      return 0
    
    def userStateChanged(self, p, current=None):
      return 0

    def channelCreated(self, c, current=None):
      return 0

    def channelRemoved(self, c, current=None):
      return 0

    def channelStateChanged(self, c, current=None):
      return 0

class ServerContextCallbackI(Murmur.ServerContextCallback):
    def __init__(self, server):
      self.server = server

    def contextAction(self, action, p, session, chanid, current=None):
      '''p = user, who clicked, session = target of clicker...'''
      global st_user
      
      if (action == "stdel"): #Remove a user out of ST list.
	  if (p.session == session): #The bad guy can't remove his own ST status :P
	      return 1
	  else:
	      UserState=self.server.getState(session)
	      if UserState.userid in st_user:
		  UserState.channel=st_user[UserState.userid]
		  del st_user[UserState.userid]
		  self.server.removeUserFromGroup(0, session, st_group) #Add user to server group.
		  self.server.setState(UserState)
		  self.server.sendMessageChannel(UserState.channel,True, msg_STremoved % (UserState.name, p.name))

      if (action == "stadd"): #Add a user to ST list.
	  UserState=self.server.getState(session)

	  if (p.session == session): #Nobody should be able to beat himself :P
	      self.server.sendMessage(p.session, "<font style='color:red;font-weight:bold;'>You can't set yourself to ST status.</font>")
	      return 1
	  if (p.userid in st_user): #A beaten user, even if admin, should not be able to beat other users while in ST status.
	      self.server.sendMessage(p.session, "<font style='color:red;font-weight:bold;'>You are in ST status, you can't set another user to ST.</font>")
	      return 1
	  if (UserState.userid in st_user): #If already in ST, don't repeat it...
	      self.server.sendMessage(p.session, "<font style='color:red;font-weight:bold;'>This user already has ST status.</font>")
	      return 1

	  UserState.channel=st_channel
	  st_user[UserState.userid] = chanid #Add user to ST list.
	  self.server.addUserToGroup(0, session, st_group) #Add user to server group.
	  self.server.setState(UserState)
	  self.server.sendMessageChannel(chanid,True, msg_STadded % (UserState.name, p.name))

if __name__ == "__main__":
    global contextR
    prop = Ice.createProperties(sys.argv)
    prop.setProperty("Ice.ImplicitContext", "Shared")
    idd = Ice.InitializationData()
    idd.properties = prop
    ice = Ice.initialize(idd)
    print "Creating callbacks...",
    # If icesecret is set, we need to set it here as well.
    ice.getImplicitContext().put("secret", icesecret)
    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy('Meta:tcp -h 127.0.0.1 -p %i' % iceport))
    adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h 127.0.0.1")
    metaR=Murmur.MetaCallbackPrx.uncheckedCast(adapter.addWithUUID(MetaCallbackI()))
    adapter.activate()
    meta.addCallback(metaR)

    server=meta.getServer(serverid)
    serverR=Murmur.ServerCallbackPrx.uncheckedCast(adapter.addWithUUID(ServerCallbackI(server, adapter)))
    server.addCallback(serverR)

    print "Done"
    print 'Script running (press CTRL-C to abort)';
    try:
        ice.waitForShutdown()
    except KeyboardInterrupt:
        print 'CTRL-C caught, aborting'

    meta.removeCallback(metaR)
    ice.shutdown()
    print "Goodbye"
