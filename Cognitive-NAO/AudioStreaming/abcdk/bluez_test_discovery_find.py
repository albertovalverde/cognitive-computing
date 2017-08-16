#!/usr/bin/python

import gobject

import dbus
import dbus.mainloop.glib
from optparse import OptionParser, make_option

global_strDeviceToFind = "";
global_bFound = False;

def device_found(address, properties):
    # print "[ " + address + " ]" + "( " + properties["Name"] + ")";
    global global_strDeviceToFind;
    if( global_strDeviceToFind != "" ):
        if( global_strDeviceToFind == properties["Name"] ):
            print( "Address:\n%s" % properties["Address"] );
            global global_bFound;
            global_bFound = True;
            mainloop.quit();
            return;
    else:
        for key in properties.keys():
            value = properties[key]
            if (key == "Class"):
                print "    %s = 0x%06x" % (key, value)
            else:
                print "    %s = %s" % (key, value)

def property_changed(name, value):
	if (name == "Discovering" and not value):
		mainloop.quit()

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
							"org.bluez.Manager")

	option_list = [
			make_option("-i", "--device", action="store", type="string", dest="dev_id"),
			make_option("-f", "--find", action="store", type="string", dest="strNameToFind"),
			];
	parser = OptionParser(option_list=option_list)

	(options, args) = parser.parse_args()
	
	if options.strNameToFind:
		global global_strDeviceToFind;
		global_strDeviceToFind = options.strNameToFind;

	if options.dev_id:
		adapter_path = manager.FindAdapter(options.dev_id)
	else:
		adapter_path = manager.DefaultAdapter()

	adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path),
							"org.bluez.Adapter")

	bus.add_signal_receiver(device_found,
			dbus_interface = "org.bluez.Adapter",
					signal_name = "DeviceFound")

	bus.add_signal_receiver(property_changed,
			dbus_interface = "org.bluez.Adapter",
					signal_name = "PropertyChanged")

	adapter.StartDiscovery()

	mainloop = gobject.MainLoop()
	mainloop.run()
	global global_bFound;
	if( not global_bFound ):
		print( "Not found!" );