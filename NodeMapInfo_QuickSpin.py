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
# NodeMapInfo_QuickSpin.py shows how to interact with nodes
# using the QuickSpin API. QuickSpin is a subset of the Spinnaker library
# that allows for simpler node access and control.
#
# This example demonstrates the retrieval of information from both the
# transport layer and the camera. Because the focus of this example is node
# access, which is where QuickSpin and regular Spinnaker differ, this
# example differs from NodeMapInfo quite a bit.
#
# A much wider range of topics is covered in the full Spinnaker examples than
# in the QuickSpin ones. There are only enough QuickSpin examples to
# demonstrate node access and to get started with the API; please see full
# Spinnaker examples for further or specific knowledge on a topic.

import PySpin


def print_transport_layer_device_info(cam):
    """
    Prints device information from the transport layer.

    *** NOTES ***
    In QuickSpin, accessing device information on the transport layer is
    accomplished via a camera's TLDevice property. The TLDevice property
    houses nodes related to general device information such as the three
    demonstrated below, device access status, XML and GUI paths and
    locations, and GEV information to name a few. The TLDevice property
    allows access to nodes that would generally be retrieved through the
    TL device nodemap in full Spinnaker.

    Notice that each node is checked for availability and readability
    prior to value retrieval. Checking for availability and readability
    (or writability when applicable) whenever a node is accessed is
    important in terms of error handling. If a node retrieval error
    occurs but remains unhandled, an exception is thrown.

    :param cam: Camera to get information from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Print device serial number
        if cam.TLDevice.DeviceSerialNumber.GetAccessMode() == PySpin.RO:
            print "Device serial number: %s" % cam.TLDevice.DeviceSerialNumber.ToString()

        else:
            print "Device serial number: unavailable"
            result = False

        # Print device vendor name
        #
        # *** NOTE ***
        # To check node readability/writability, you can either
        # compare its access mode with RO, RW, etc. or you can use
        # the IsReadable/IsWritable functions on the node.
        if PySpin.IsReadable(cam.TLDevice.DeviceVendorName):
            print "Device vendor name: %s" % cam.TLDevice.DeviceVendorName.ToString()
        else:
            print "Device vendor name: unavailable"
            result = False

        # Print device display name
        if PySpin.IsReadable(cam.TLDevice.DeviceDisplayName):
            print "Device display name: %s" % cam.TLDevice.DeviceDisplayName.ToString()
        else:
            print "Device display name: unavailable"
            result = False

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_transport_layer_stream_info(cam):
    """
    Prints stream information from transport layer.

    *** NOTES ***
    In QuickSpin, accessing stream information on the transport layer is
    accomplished via a camera's TLStream property. The TLStream property
    houses nodes related to streaming such as the two demonstrated below,
    buffer information, and GEV packet information to name a few. The
    TLStream property allows access to nodes that would generally be
    retrieved through the TL stream nodemap in full Spinnaker.

    :param cam: Camera to get information from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Print stream ID
        if cam.TLStream.StreamID.GetAccessMode() == PySpin.RO:
            print "Stream ID: %s" % cam.TLStream.StreamID.ToString()
        else:
            print "Stream ID: unavailable"
            result = False

        # Print stream type
        if PySpin.IsReadable(cam.TLStream.StreamType):
            print "Stream type: %s" % cam.TLStream.StreamType.ToString()
        else:
            print "Stream type: unavailable"
            result = False

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_transport_layer_interface_info(interface):
    """
    Prints stream information from the transport layer.

    *** NOTES ***
    In QuickSpin, accessing interface information is accomplished via an
    interface's TLInterface property. The TLInterface property houses
    nodes that hold information about the interface such as the three
    demonstrated below, other general interface information, and
    GEV addressing information. The TLInterface property allows access to
    nodes that would generally be retrieved through the interface nodemap
    in full Spinnaker.

    Interface nodes should also always be checked for availability and
    readability (or writability when applicable). If a node retrieval
    error occurs but remains unhandled, an exception is thrown.

    :param interface: Interface to get information from.
    :type interface: InterfacePtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Print interface display name
        if interface.TLInterface.InterfaceDisplayName.GetAccessMode() == PySpin.RO:
            print "Interface display name: %s" % interface.TLInterface.InterfaceDisplayName.ToString()
        else:
            print "Interface display name: unavailable"
            result = False

        # Print interface ID
        if interface.TLInterface.InterfaceID.GetAccessMode() == PySpin.RO:
            print "Interface ID: %s" % interface.TLInterface.InterfaceID.ToString()
        else:
            print "Interface ID: unavailable"
            result = False

        # Print interface type
        if PySpin.IsReadable(interface.TLInterface.InterfaceType.GetAccessMode()):
            print "Interface type: %s" % interface.TLInterface.InterfaceType.ToString()
        else:
            print "Interface type: unavailable"
            result = False

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_genicam_device_info(cam):
    """
    Prints device information from the camera.

    *** NOTES ***
    Most camera interaction happens through GenICam nodes. The
    advantages of these nodes is that there is a lot more of them, they
    allow for a much deeper level of interaction with a camera, and no
    intermediate property (i.e. TLDevice or TLStream) is required. The
    disadvantage is that they require initialization.

    :param cam: Camera to get information from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Print exposure time
        if cam.ExposureTime.GetAccessMode() == PySpin.RO or cam.ExposureTime.GetAccessMode() == PySpin.RW:
            print "Exposure time: %s" % cam.ExposureTime.ToString()
        else:
            print "Exposure time: unavailable"
            result = False

        # Print black level
        if PySpin.IsReadable(cam.BlackLevel):
            print "Black level: %s" % cam.BlackLevel.ToString()
        else:
            print "Black level: unavailable"
            result = False

        # Print height
        if PySpin.IsReadable(cam.Height):
            print "Height: %s" % cam.Height.ToString()
        else:
            print "Height: unavailable"
            result = False

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def main():
    """
    Example entry point; this function prints transport layer information from
    each interface and transport and GenICam information from each camera.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    sys = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = sys.GetCameras()

    num_cams = len(cam_list)

    print "Number of cameras detected: %i \n" % num_cams

    # Retrieve list of interfaces from the system 
    iface_list = sys.GetInterfaces()

    num_ifaces = iface_list.GetSize()

    print "Number of interfaces detected: %i \n" % num_ifaces

    # Print information on each interface
    #
    # *** NOTES ***
    # All USB 3 Vision and GigE Vision interfaces should enumerate for
    # Spinnaker.
    print "\n*** PRINTING INTERFACE INFORMATION ***\n"

    for i in range(num_ifaces):
        result &= print_transport_layer_interface_info(iface_list[i])

    # Print general device information on each camera from transport layer
    #
    # *** NOTES ***
    # Transport layer nodes do not require initialization in order to interact
    # with them.
    print "\n*** PRINTING TRANSPORT LAYER DEVICE INFORMATION ***\n"

    for i in range(num_cams):
        result &= print_transport_layer_device_info(cam_list[i])

    # Print streaming information on each camera from transport layer
    #
    # *** NOTES ***
    # Again, initialization is not required to print information from the
    # transport layer; this is equally true of streaming information.
    print "\n*** PRINTING TRANSPORT LAYER STREAMING INFORMATION ***\n"

    for i in range(num_cams):
        result &= print_transport_layer_stream_info(cam_list[i])

    # Print device information on each camera from GenICam nodemap
    #
    # *** NOTES ***
    # GenICam nodes require initialization in order to interact with
    # them; as such, this loop initializes the camera, prints some information
    # from the GenICam nodemap, and then deinitializes it. If the camera were
    # not initialized, node availability would fail.
    print "\n*** PRINTING GENICAM INFORMATION ***\n"

    # NOTE: The CameraList can be iterated over without using an index to grab each camera.
    for cam in cam_list:
        # Initialize camera
        cam.Init()

        # Print info
        result &= print_genicam_device_info(cam)

        # Deinitialize camera
        cam.DeInit()

    # Delete any references to camera
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Clear interface list before releasing system
    iface_list.Clear()

    # Release system
    sys.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")
    return result

if __name__ == "__main__":
    main()
