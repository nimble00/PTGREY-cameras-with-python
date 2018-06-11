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
#   Enumeration_QuickSpin.py shows how to enumerate interfaces
#   and cameras using the QuickSpin API. QuickSpin is a subset of the Spinnaker
#   library that allows for simpler node access and control. This is a great
#   example to start learning about QuickSpin.
#
#  	This example introduces the preparation, use, and cleanup of the system
#  	object, interface and camera lists, interfaces, and cameras. It also
#  	touches on retrieving information from pre-fetched nodes using QuickSpin.
#  	Retrieving node information is the only portion of the example that
#  	differs from Enumeration.
#
#   A much wider range of topics is covered in the full Spinnaker examples than
#   in the QuickSpin ones. There are only enough QuickSpin examples to
#   demonstrate node access and to get started with the API; please see full
#   Spinnaker examples for further or specific knowledge on a topic.

import PySpin


def query_interface(interface):
    """
    Queries an interface for its cameras and prints out device information.

    :param interface: InterfacePtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    try:
        result = True

        # Print interface display name
        #
        # *** NOTES ***
        # QuickSpin allows for the retrieval of interface information directly
        # from an interface. Because interface information is made available
        # on the transport layer, camera initialization is not required.
        node_interface_display_name = interface.TLInterface.InterfaceDisplayName
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
            return True

        # Print device vendor and model name for each camera on the interface
        for i in range(num_cams):

            # Select camera
            #
            # *** NOTES ***
            # Each camera is retrieved from a camera list with an index. If
            # the index is out of range, an exception is thrown.
            cam = cam_list[i]

            # Print device vendor name and device model name
            #
            # *** NOTES ***
            # In QuickSpin, accessing nodes does not require first retrieving a
            # nodemap. Instead, GenICam nodes are made available
            # directly through the camera, and transport layer nodes are made
            # available through the camera's TLDevice and TLStream properties.
            #
            # Most camera interaction happens through the GenICam nodemap, which
            # requires the device to be initialized. Simpler reads, like the
            # ones below, can often be accomplished at the transport layer,
            # which does not require initialization; please see
            # NodeMapInfo_QuickSpin for additional information on this topic.
            #
            # Readability/writability should be checked prior to interacting with
            # nodes. Readability and writability are ensured by checking the
            # access mode or by using the methods
            if cam.TLDevice.DeviceVendorName.GetAccessMode() == PySpin.RO:
                device_vendor_name = cam.TLDevice.DeviceVendorName.ToString()

            if cam.TLDevice.DeviceModelName.GetAccessMode() == PySpin.RO:
                device_model_name = cam.TLDevice.DeviceModelName.GetValue()

            print "\tDevice %i %s %s \n" % (i, device_vendor_name, device_model_name)

        # Clear camera list before losing scope
        #
        # *** NOTES ***
        # Camera lists (and interface lists) must be cleared manually while in
        # the same scope that the system is released. However, in cases like this
        # where scope is lost, camera lists (and interface lists) will be cleared
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
    # that unreleased resources and still registered events will throw an
    # exception.
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")

if __name__ == "__main__":
    main()