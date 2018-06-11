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
#  NodeMapCallback.py shows how to use nodemap callbacks. It relies
#  on information provided in the Enumeration, Acquisition, and NodeMapInfo
#  examples. As callbacks are very similar to events, it may be a good idea to
#  explore this example prior to tackling the events examples.
#
#  This example focuses on creating, registering, using, and unregistering
#  callbacks. A callback requires a callback class with a callback function signature,
#  which allows it to be registered to and access a node. Events follow this same pattern.
#
#  Once comfortable with NodeMapCallback, we suggest checking out any of the
#  events examples: DeviceEvents, EnumerationEvents, ImageEvents, or Logging.

import PySpin


class HeightNodeCallback(PySpin.NodeCallback):
    """
    This is the first of two callback classes.  This callback will be registered to the height node.
    Node callbacks must inherit from NodeCallback, and must implement CallbackFunction with the same function signature.

    NOTE: Instances of callback classes must not go out of scope until they are deregistered, otherwise segfaults
    will occur.
    """
    def __init__(self):
        super(HeightNodeCallback, self).__init__()

    def CallbackFunction(self, node):
        """
        This function gets called when the height node changes and triggers a callback.

        :param node: Height node.
        :type node: INode
        :rtype: None
        """
        node_height = PySpin.CIntegerPtr(node)
        print "Height callback message:\n\tLook! Height changed to %f...\n" % node_height.GetValue()


class GainNodeCallback(PySpin.NodeCallback):
    """
    This is the second callback class, registered to the gain node.
    """
    def __init__(self):
        super(GainNodeCallback, self).__init__()

    def CallbackFunction(self, node):
        """
        This function gets called when the gain node changes and triggers a callback.

        :param node: Gain node.
        :type node: INode
        :rtype: None
        """
        node_gain = PySpin.CFloatPtr(node)
        print "Gain callback message:\n\tLook! Gain changed to %f...\n" % node_gain.GetValue()


def configure_callbacks(nodemap):
    """
    This function sets up the example by disabling automatic gain, creating the callbacks, and registering them to
    their specific nodes.

    :param nodemap: Device nodemap.
    :type nodemap: INodeMap
    :returns: tuple (result, callback_height, callback_gain)
        WHERE
        result is True if successful, False otherwise
        callback_height is the HeightNodeCallback instance registered to the height node
        callback_gain is the GainNodeCallback instance registered to the gain node
    :rtype: (bool, HeightNodeCallback, GainNodeCallback)
    """
    print "\n*** CONFIGURING CALLBACKS ***\n"
    try:
        result = True

        # Turn off automatic gain
        #
        # *** NOTES ***
        # Automatic gain prevents the manual configuration of gain and needs to
        # be turned off for this example.
        #
        # *** LATER ***
        # Automatic exposure is turned off at the end of the example in order
        # to restore the camera to its default state.
        node_gain_auto = PySpin.CEnumerationPtr(nodemap.GetNode("GainAuto"))
        if not PySpin.IsAvailable(node_gain_auto) or not PySpin.IsWritable(node_gain_auto):
            print "Unable to disable automatic gain (node retrieval). Aborting..."
            return False

        node_gain_auto_off = PySpin.CEnumEntryPtr(node_gain_auto.GetEntryByName("Off"))
        if not PySpin.IsAvailable(node_gain_auto_off) or not PySpin.IsReadable(node_gain_auto_off):
            print "Unable to disable automatic gain (enum entry retrieval). Aborting..."
            return False

        node_gain_auto.SetIntValue(node_gain_auto_off.GetValue())
        print "Automatic gain disabled..."

        # Register callback to height node
        #
        # *** NOTES ***
        # Callbacks need to be registered to nodes, which should be writable
        # if the callback is to ever be triggered. Also ensure that the callback
        # instance does not go out of scope, as it will get garbage-collected
        # and a segfault will result once the callback actually occurs.
        #
        # *** LATER ***
        # Each callback needs to be unregistered individually before releasing
        # the system or an exception will be thrown.
        node_height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))
        if not PySpin.IsAvailable(node_height) or not PySpin.IsWritable(node_height):
            print "Unable to retrieve height. Aborting...\n"
            return False

        print "Height ready..."

        callback_height = HeightNodeCallback()
        PySpin.RegisterNodeCallback(node_height.GetNode(), callback_height)

        print "Height callback registered..."

        # Register callback to gain node
        #
        # *** NOTES ***
        # Depending on the specific goal of the function, it can be important
        # to notice the node type that a callback is registered to. Notice in
        # the callback functions above that the callback registered to height
        # casts its node as an integer whereas the callback registered to gain
        # casts as a float.
        #
        # *** LATER ***
        # Each callback needs to be unregistered individually before releasing
        # the system or an exception will be thrown.
        node_gain = PySpin.CFloatPtr(nodemap.GetNode("Gain"))
        if not PySpin.IsAvailable(node_gain) or not PySpin.IsWritable(node_gain):
            print "Unable to retrieve gain. Aborting...\n"
            return False

        print "Gain ready..."

        callback_gain = GainNodeCallback()
        PySpin.RegisterNodeCallback(node_gain.GetNode(), callback_gain)
        print "Gain callback registered...\n"

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result, callback_height, callback_gain


def change_height_and_gain(nodemap):
    """
    This function demonstrates the triggering of the nodemap callbacks. First it
    changes height, which executes the callback registered to the height node, and
    then it changes gain, which executes the callback registered to the gain node.

    :param nodemap: Device nodemap.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print "\n***CHANGE HEIGHT & GAIN ***\n"

    try:
        result = True

        # Change height to trigger height callback
        # 
        # *** NOTES ***
        # Notice that changing the height only triggers the callback function
        # registered to the height node.
        node_height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))
        if not PySpin.IsAvailable(node_height) or not PySpin.IsWritable(node_height) \
                or node_height.GetInc() == 0 or node_height.GetMax() == 0:

            print "Unable to retrieve height. Aborting..."
            return False

        height_to_set = node_height.GetMax()

        print "Regular function message:\n\tHeight about to be changed to %i...\n" % height_to_set

        node_height.SetValue(height_to_set)

        # Change gain to trigger gain callback
        #
        # *** NOTES ***
        # The same is true of changing the gain node; changing a node will
        # only ever trigger the callback function (or functions) currently
        # registered to it.
        node_gain = PySpin.CFloatPtr(nodemap.GetNode("Gain"))
        if not PySpin.IsAvailable(node_gain) or not PySpin.IsWritable(node_gain) or node_gain.GetMax() == 0:
            print "Unable to retrieve gain..."
            return False

        gain_to_set = node_gain.GetMax() / 2.0

        print "Regular function message:\n\tGain about to be changed to %f...\n" % gain_to_set
        node_gain.SetValue(gain_to_set)

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def reset_callbacks(nodemap, callback_height, callback_gain):
    """
    This function cleans up the example by deregistering the callbacks and 
    turning automatic gain back on.

    :param nodemap: Device nodemap.
    :param callback_height: Height node callback instance to deregister.
    :param callback_gain: Gain node callback instance to deregister.
    :type nodemap: INodeMap
    :type callback_height: HeightNodeCallback
    :type callback_gain: GainNodeCallback
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Deregister callbacks
        #
        # *** NOTES ***
        # It is important to deregister each callback function from each node
        # that it is registered to.
        PySpin.DeregisterNodeCallback(callback_height)
        PySpin.DeregisterNodeCallback(callback_gain)

        print "Callbacks deregistered..."

        # Turn automatic gain back on
        # 
        # *** NOTES ***
        # Automatic gain is turned back on in order to restore the camera to 
        # its default state.
        node_gain_auto = PySpin.CEnumerationPtr(nodemap.GetNode("GainAuto"))
        if not PySpin.IsAvailable(node_gain_auto) or not PySpin.IsWritable(node_gain_auto):
            print "Unable to enable automatic gain (node retrieval). Aborting..."
            return False

        node_gain_auto_continuous = PySpin.CEnumEntryPtr(node_gain_auto.GetEntryByName("Continuous"))
        if not PySpin.IsAvailable(node_gain_auto_continuous) or not PySpin.IsReadable(node_gain_auto_continuous):
            print "Unable to enable automatic gain (enum entry retrieval). Aborting..."
            return False

        node_gain_auto.SetIntValue(node_gain_auto_continuous.GetValue())
        print "Automatic gain disabled..."

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print "*** DEVICE INFORMATION ***\n"

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode("DeviceInformation"))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print "%s: %s" % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else "Node not readable")

        else:
            print "Device control information not available."

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to setup and run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Configure callbacks
        err, callback_height, callback_gain = configure_callbacks(nodemap)
        if not err:
            return err

        # Change height and gain to trigger callbacks
        result &= change_height_and_gain(nodemap)

        # Reset callbacks
        result &= reset_callbacks(nodemap, callback_height, callback_gain)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print "Number of cameras detected: %d" % num_cameras

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system
        system.ReleaseInstance()

        print "Not enough cameras!"
        raw_input("Done! Press Enter to exit...")
        return False

    # Run example on each camera
    for i in range(num_cameras):
        cam = cam_list.GetByIndex(i)

        print "Running example for camera %d..." % i

        result &= run_single_camera(cam)
        print "Camera %d example complete..." % i

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system

    cam_list.Clear()

    # Release instance
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")
    return result

if __name__ == "__main__":
    main()
