# coding=utf-8
# =============================================================================
#  Copyright © 2017 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
#
#  This software is the confidential and proprietary information of FLIR
#  Integrated Imaging Solutions, Inc. ("Confidential Information"). You
#  shall not disclose such Confidential Information and shall use it only in
#  accordance with the terms of the license agreement you entered into
#  with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
#  FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
#  SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
#  SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
#  THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
#  	EnumerationEvents.py explores arrival and removal events on interfaces and the system.
#   It relies on information provided in the Enumeration, Acquisition, and NodeMapInfo examples.
#
#  	It can also be helpful to familiarize yourself with the NodeMapCallback example,
#   as nodemap callbacks follow the same general procedure as events, but with a few less steps.
#
#  	This example creates two user-defined classes: InterfaceEventHandler and SystemEventHandler.
#   These child classes allow the user to define properties, parameters, and the event itself
#   while the parent classes - ArrivalEvent, RemovalEvent, and InterfaceEvent -
#   allow the child classes to interface with Spinnaker.

import PySpin


class InterfaceEventHandler(PySpin.InterfaceEvent):
    """
    This class defines the properties and methods for device arrivals and removals
    on an interface. Take special note of the signatures of the OnDeviceArrival()
    and OnDeviceRemoval() methods. Also, enumeration events must inherit from
    InterfaceEvent whether they are to be registered to the system or an interface.
    """
    def __init__(self, iface, iface_num):
        """
        Constructor. Note that this sets the interface instance.

        :param iface: Interface instance.
        :param iface_num: Interface number.
        """
        super(InterfaceEventHandler, self).__init__()
        self.interface = iface
        self.interface_num = iface_num

    def OnDeviceArrival(self, serial_number):
        """
        This method defines the arrival event on an interface. It prints out
        the device serial number of the camera arriving and the interface
        number. The argument is the serial number of the camera that triggered
        the arrival event.

        :param serial_number: gcstring representing the device serial number of arriving camera
        :type serial_number: gcstring
        :return: None
        """
        print "Interface event handler:"
        print "\tDevice %i has arrived on interface %i." % (serial_number, self.interface_num)
        
    def OnDeviceRemoval(self, serial_number):
        """
        This method defines removal events on an interface. It prints out the
        device serial number of the camera being removed and the interface
        number. The argument is the serial number of the camera that triggered
        the removal event.

        :param serial_number: gcstring representing the device serial number of removed camera
        :type serial_number: gcstring
        :return: None
        """
        print "Interface event handler:"
        print "\tDevice %i was removed from interface %i." % (serial_number, self.interface_num)
    
    
class SystemEventHandler(PySpin.InterfaceEvent):
    """
    In the C++ example, the SystemEventHandler inherits from both ArrivalEvent and
    RemovalEvent. This doesn't work for this wrapper, as it will only inherit the abstract
    method from the first base class listed, so for this example both System and Interface
    event handlers inherit from InterfaceEvent.
    All three event types - ArrivalEvent, RemovalEvent, and InterfaceEvent - can be
    registered to interfaces, the system, or both.
    """
    def __init__(self, system):
        """
        Constructor. This sets the system instance.

        :param system: Instance of the system.
        :type system: SystemPtr
        :rtype: None
        """
        super(SystemEventHandler, self).__init__()
        self.system = system

    def OnDeviceArrival(self, serial_number):
        """
        This method defines the arrival event on the system. It retrieves the
        number of cameras currently connected and prints it out.

        :param serial_number: gcstring representing the serial number of the arriving camera.
        :type serial_number: gcstring
        :return: None
        """
        cam_list = self.system.GetCameras()
        count = cam_list.GetSize()
        print "System event handler:"
        print "\tThere %s %i %s on the system." % ("is" if count == 1 else "are",
                                                   count,
                                                   "device" if count == 1 else "devices")

    def OnDeviceRemoval(self, serial_number):
        """
        This method defines the removal event on the system. It does the same
        as the system arrival event - it retrieves the number of cameras
        currently connected and prints it out.

        :param serial_number: gcstring representing the serial number of the removed camera.
        :type serial_number: gcstring
        :return: None
        """
        cam_list = self.system.GetCameras()
        count = cam_list.GetSize()
        print "System event handler:"
        print "\tThere %s %i %s on the system." % ("is" if count == 1 else "are",
                                                   count,
                                                   "device" if count == 1 else "devices")


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :rtype: None
    """
    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()
    
    num_cams = cam_list.GetSize()
    
    print "Number of cameras detected: %i" % num_cams

    # Retrieve list of interfaces from the system
    interface_list = system.GetInterfaces()

    num_ifaces = interface_list.GetSize()

    print "Number of interfaces detected: %i" % num_ifaces

    print "*** CONFIGURING ENUMERATION EVENTS *** \n"

    # Create interface event for the system
    #
    # *** NOTES ***
    # The SystemEventHandler has been constructed to accept a system object in
    # order to print the number of cameras on the system.
    system_event_handler = SystemEventHandler(system)

    # Register interface event for the system
    #
    # *** NOTES ***
    # Arrival, removal, and interface events can all be registered to
    # interfaces or the system. Do not think that interface events can only be
    # registered to an interface. An interface event is merely a combination
    # of an arrival and a removal event.
    #
    # *** LATER ***
    # Arrival, removal, and interface events must all be unregistered manually.
    # This must be done prior to releasing the system and while they are still
    # in scope.
    system.RegisterInterfaceEvent(system_event_handler)

    # Create and register interface event to each interface
    #
    # *** NOTES ***
    # The process of event creation and registration on interfaces is similar
    # to the process of event creation and registration on the system. The
    # class for interfaces has been constructed to accept an interface and an
    # interface number (this is just to separate the interfaces).
    #
    # *** LATER ***
    # Arrival, removal, and interface events must all be unregistered manually.
    # This must be done prior to releasing the system and while they are still
    # in scope.
    interface_events = []

    for i in range(num_ifaces):

        # Select interface
        iface = interface_list[i]

        # Create interface event
        iface_event_handler = InterfaceEventHandler(iface, i)
        interface_events.append(iface_event_handler)

        # Register interface event
        iface.RegisterEvent(interface_events[i])

        print "Event handler registered to interface %i ..." % i

    # Delete references to interface
    del iface
    del iface_event_handler

    # Wait for user to plug in and/or remove camera devices
    raw_input("\nReady! Remove/Plug in cameras to test or press Enter to exit...\n")

    # Unregister interface event from each interface
    #
    # *** NOTES ***
    # It is important to unregister all arrival, removal, and interface events
    # from all interfaces that they may be registered to.
    for i in range(num_ifaces):
        interface_list[i].UnregisterEvent(interface_events[i])

    # Delete all interface events, which each have a reference to an interface
    del interface_events
    print "Event handler unregistered from interfaces..."

    # Unregister system event from system object
    #
    # *** NOTES ***
    # It is important to unregister all arrival, removal, and interface events
    # registered to the system.
    system.UnregisterInterfaceEvent(system_event_handler)

    # Delete system event, which has a system reference
    del system_event_handler
    print "Event handler unregistered from system..."

    # Clear camera list before releasing system
    cam_list.Clear()

    # Clear interface list before releasing system
    interface_list.Clear()

    # Release system
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")

if __name__ == "__main__":
    main()
