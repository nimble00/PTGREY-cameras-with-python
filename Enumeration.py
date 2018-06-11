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
#   Enumeration.py shows how to enumerate interfaces and cameras.
#  	Knowing this is mandatory for doing anything with the Spinnaker SDK, and is
#  	therefore the best place to start learning how to use the SDK.
#
#  	This example introduces the preparation, use, and cleanup of the system
#  	object, interface and camera lists, interfaces, and cameras. It also touches
#  	on retrieving both nodes from nodemaps and information from nodes.
#
#  	Once comfortable with enumeration, we suggest checking out the Acquisition and/or
#   NodeMapInfo examples. Acquisition demonstrates using a camera to acquire images,
#   and NodeMapInfo demonstrates retrieving information from various node types.
import pyspin
from pyspin import PySpin


def query_interface(interface):
    """
    Queries an interface for its cameras and prints out device information.

    :param interface: InterfacePtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    try:
        result = True

        # Retrieve TL nodemap from interface
        #
        # *** NOTES ***
        # Each interface has a nodemap that can be retrieved in order to
        # access information about the interface itself, any devices
        # connected, or addressing information if applicable.
        nodemap_interface = interface.GetTLNodeMap()

        # Print interface display name
        #
        # *** NOTES ***
        # Grabbing node information requires first retrieving the node and
        # then retrieving its information. There are two things to keep in
        # mind. First, a node is distinguished by type, which is related
        # to its value's data type. Second, nodes should be checked for
        # availability and readability/writability prior to making an
        # attempt to read from or write to the node.
        #
        # Note that for Python, the node retrieved then has to be 'cast'
        # to the proper type (CStringPtr in this case) before it can be used.
        node_interface_display_name = PySpin.CStringPtr(nodemap_interface.GetNode("InterfaceDisplayName"))

        if PySpin.IsAvailable(node_interface_display_name) and PySpin.IsReadable(node_interface_display_name):
            interface_display_name = node_interface_display_name.GetValue()

            print interface_display_name

        else:
            print "Interface display name not readable"

        # Update list of cameras on the interface
        #
        # *** NOTES ***
        # Updating the cameras on each interface is especially important if
        # there has been any device arrivals or removals since the last time
        # that UpdateCameras() was called.
        interface.UpdateCameras()

        # Retrieve list of cameras from the interface
        #
        # *** NOTES ***
        # Camera lists can be retrieved from an interface or the system object.
        # Camera lists retrieved from an interface, such as this one, only
        # return cameras attached on that specific interface whereas camera
        # lists retrieved from the system will return all cameras on all
        # interfaces.
        #
        # *** LATER ***
        # Camera lists must be cleared manually. This must be done prior to
        # releasing the system and while the camera list is still in scope.
        cam_list = interface.GetCameras()

        # Retrieve number of cameras
        num_cams = cam_list.GetSize()

        # Return if no cameras detected
        if num_cams == 0:
            print "\tNo devices detected.\n"
            return result

        # Print device vendor and model name for each camera on the interface
        for i in range(num_cams):

            # Select camera
            #
            # *** NOTES ***
            # Each camera is retrieved from a camera list with an index. If
            # the index is out of range, an exception is thrown.
            cam = cam_list[i]

            # Retrieve TL device nodemap; please see NodeMapInfo example for
            # additional comments on transport layer nodemaps
            nodemap_tldevice = cam.GetTLDeviceNodeMap()

            # Print device vendor name and device model name
            #
            # *** NOTES ***
            # Grabbing node information requires first retrieving the node and
            # then retrieving its information. There are two things to keep in
            # mind. First, a node is distinguished by type, which is related
            # to its value's data type. Second, nodes should be checked for
            # availability and readability/writability prior to making an
            # attempt to read from or write to the node.
            node_device_vendor_name = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceVendorName"))

            if PySpin.IsAvailable(node_device_vendor_name) and PySpin.IsReadable(node_device_vendor_name):
                device_vendor_name = node_device_vendor_name.ToString()

            node_device_model_name = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceModelName"))

            if PySpin.IsAvailable(node_device_model_name) and PySpin.IsReadable(node_device_model_name):
                device_model_name = node_device_model_name.ToString()

            print "\tDevice %i %s %s \n" % (i, device_vendor_name, device_model_name)

        # Clear camera list before losing scope
        #
        # *** NOTES ***
        # Camera lists (and interface lists) must be cleared manually while in
        # the same scope that the system is released. However, in cases like this
        # where scope is lost, camera lists (and interface lists) will be cleared
        # automatically.
        cam_list.Clear()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def main():
    """
    Example entry point.
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    #
    # *** NOTES ***
    # Everything originates with the system object. It is important to notice
    # that it has a singleton implementation, so it is impossible to have
    # multiple system objects at the same time. Users can only get a smart
    # pointer (SystemPtr) to the system instance.
    #
    # *** LATER ***
    # The system object should be cleared prior to program completion. If not
    # released explicitly, it will be released automatically when all SystemPtr
    # objects that point to the system go out of scope.
    system = PySpin.System.GetInstance()

    # Retrieve list of interfaces from the system
    #
    # *** NOTES ***
    # Interface lists are retrieved from the system object.
    #
    # *** LATER ***
    # Interface lists must be cleared manually. This must be done prior to
    # releasing the system and while the interface list is still in scope.
    interface_list = system.GetInterfaces()

    # Get number of interfaces
    num_interfaces = interface_list.GetSize()

    print "Number of interfaces detected: %i" % num_interfaces

    # Retrieve list of cameras from the system
    #
    # *** NOTES ***
    # Camera lists can be retrieved from an interface or the system object.
    # Camera lists retrieved from the system, such as this one, return all
    # cameras available on the system.
    #
    # *** LATER ***
    # Camera lists must be cleared manually. This must be done prior to
    # releasing the system and while the camera list is still in scope.
    cam_list = system.GetCameras()

    num_cams = cam_list.GetSize()

    print "Number of cameras detected: %i" % num_cams

    # Finish if there are no cameras
    if num_cams == 0 or num_interfaces == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Clear interface list before releasing system
        interface_list.Clear()

        # Release system
        system.ReleaseInstance()

        print "Not enough cameras!"
        raw_input("Done! Press Enter to exit...")

    print "\n*** QUERYING INTERFACES ***\n"

    for i in range(num_interfaces):

        # Select interface
        #
        # *** LATER ***
        # Interfaces have to be manually deleted before the system gets released.
        # Unlike C++, the interface will not be destroyed when it goes out of the scope of this for loop;
        # instead, it gets garbage-collected at the end of main().
        interface = interface_list[i]

        # Query interface
        result &= query_interface(interface)

    # Release interface
    del interface

    # Clear camera list before releasing system
    #
    # *** NOTES ***
    # Camera lists must be cleared manually prior to a system release call.
    cam_list.Clear()

    # Clear interface list before releasing system
    #
    # *** NOTES ***
    # Interface lists must be cleared manually prior to a system release call.
    interface_list.Clear()

    # Release system
    #
    # *** NOTES ***
    # The system should be released, but if it is not, it will do so itself.
    # It is often at the release of the system (whether manual or automatic)
    # that unreleased resources and still-registered events will throw an
    # exception.
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")

if __name__ == "__main__":
    main()
