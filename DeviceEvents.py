# coding=utf-8
# =============================================================================
#  Copyright © 2017 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
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
# =============================================================================*/
#
#  DeviceEvents.py shows how to create a handler to access device
#  events. It relies on information provided in the Enumeration, Acquisition,
#  and NodeMapInfo examples.
#
#  It can also be helpful to familiarize yourself with the NodeMapCallback
#  example, as nodemap callbacks follow the same general procedure as events.
#
#  Device events can be thought of as camera-related events. This example
#  creates a user-defined class, DeviceEventHandler, which allows the user to
#  define any properties, parameters, and the event itself while DeviceEvent,
#  the parent class, allows the child class to appropriately interface with
#  the Spinnaker SDK.

import PySpin


class EventType:
    """
    'Enum' for choosing whether to register a event specifically for exposure end events
    or universally for all events.
    """
    GENERIC = 0
    SPECIFIC = 1

CHOSEN_EVENT = EventType.GENERIC  # change me!
NUM_IMAGES = 10  # number of images to acquire


class DeviceEventHandler(PySpin.DeviceEvent):
    """
    This class defines the properties, parameters, and the event itself. Take a
    moment to notice what parts of the class are mandatory, and what have been
    added for demonstration purposes. First, any class used to define device
    events must inherit from DeviceEvent. Second, the method signature of
    OnDeviceEvent() must also be consistent. Everything else - including the
    constructor, destructor, properties, and body of OnDeviceEvent() - are
    particular to the example.
    """
    def __init__(self, eventname):
        """
        This constructor registers an event name to be used on device events.

        :param eventname: Name of event to register.
        :type eventname: str
        :rtype: None
        """
        super(DeviceEventHandler, self).__init__()
        self.event_name = eventname
        self.count = 0

    def OnDeviceEvent(self, eventname):
        """
        Callback function when a device event occurs.
        Note eventname is a wrapped gcstring, not a Python string, but basic operations such as printing and comparing
        with Python strings are supported.

        :param eventname: gcstring representing the name of the occurred event.
        :type eventname: gcstring
        :rtype: None
        """
        if eventname == self.event_name:
            self.count += 1

            # Print information on specified device event
            print "\tDevice event %s with ID %i number %i..." % (self.GetDeviceEventName(),
                                                               self.GetDeviceEventId(),
                                                               self.count)
        else:
            # Print no information on non-specified event
            print "\tDevice event occurred; not %s; ignoring..." % self.event_name


def configure_device_events(nodemap, cam):
    """
    This function configures the example to execute device events by enabling all
    types of device events, and then creating and registering a device event that
    only concerns itself with an end of exposure event.

    :param INodeMap nodemap: Device nodemap.
    :param CameraPtr cam: Pointer to camera.
    :returns: tuple (result, device_event_handler)
        WHERE
        result is True if successful, False otherwise
        device_event_handler is the event handler
    :rtype: (bool, DeviceEventHandler)
    """
    print "\n*** CONFIGURING DEVICE EVENTS ***\n"

    try:
        result = True
        
        #  Retrieve device event selector
        #
        #  *** NOTES ***
        #  Each type of device event must be enabled individually. This is done
        #  by retrieving "EventSelector" (an enumeration node) and then enabling
        #  the device event on "EventNotification" (another enumeration node).
        #
        #  This example only deals with exposure end events. However, instead of
        #  only enabling exposure end events with a simpler device event function,
        #  all device events are enabled while the device event handler deals with
        #  ensuring that only exposure end events are considered. A more standard
        #  use-case might be to enable only the events of interest.
        node_event_selector = PySpin.CEnumerationPtr(nodemap.GetNode("EventSelector"))
        if not PySpin.IsAvailable(node_event_selector) or not PySpin.IsReadable(node_event_selector):
            print "Unable to retrieve event selector entries. Aborting..."
            return False

        entries = node_event_selector.GetEntries()
        print "Enabling event selector entries..."

        # Enable device events
        #
        # *** NOTES ***
        # In order to enable a device event, the event selector and event
        # notification nodes (both of type enumeration) must work in unison.
        # The desired event must first be selected on the event selector node
        # and then enabled on the event notification node.
        for entry in entries:

            # Select entry on selector node
            node_entry = PySpin.CEnumEntryPtr(entry)
            if not PySpin.IsAvailable(node_entry) or not PySpin.IsReadable(node_entry):

                # Skip if node fails
                result = False
                continue

            node_event_selector.SetIntValue(node_entry.GetValue())

            # Retrieve event notification node (an enumeration node)
            node_event_notification = PySpin.CEnumerationPtr(nodemap.GetNode("EventNotification"))
            if not PySpin.IsAvailable(node_event_notification) or not PySpin.IsWritable(node_event_notification):

                # Skip if node fails
                result = False
                continue

            # Retrieve entry node to enable device event
            node_event_notification_on = PySpin.CEnumEntryPtr(node_event_notification.GetEntryByName("On"))
            if not PySpin.IsAvailable(node_event_notification_on) or not PySpin.IsReadable(node_event_notification_on):

                # Skip if node fails
                result = False
                continue

            node_event_notification.SetIntValue(node_event_notification_on.GetValue())

            print "\t%s: enabled..." % node_entry.GetDisplayName()

        # Create device event
        #
        # *** NOTES ***
        # The class has been designed to take in the name of an event. If all
        # events are registered generically, all event types will trigger a
        # device event; on the other hand, if an event is registered
        # specifically, only that event will trigger an event.
        device_event_handler = DeviceEventHandler("EventExposureEnd")

        # Register device event
        #
        # *** NOTES ***
        # Device events are registered to cameras. If there are multiple
        # cameras, each camera must have any device events registered to it
        # separately. Note that multiple device events may be registered to a
        # single camera.
        #
        # *** LATER ***
        # Device events must be unregistered manually. This must be done prior
        # to releasing the system and while the device events are still in
        # scope.
        if CHOSEN_EVENT == EventType.GENERIC:

            # Device event handlers registered generally will be triggered by any device events.
            cam.RegisterEvent(device_event_handler)

            print "Device event handler registered generally..."

        elif CHOSEN_EVENT == EventType.SPECIFIC:

            # Device event handlers registered to a specified event will only
            # be triggered by the type of event is it registered to.
            cam.RegisterEvent(device_event_handler, "EventExposureEnd")

            print "Device event handler registered specifically to EventExposureEnd events..."

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result, device_event_handler


def reset_device_events(cam, device_event_handler):
    """
    This function resets the example by unregistering the device event.

    :param cam: Camera to unregister event handler from.
    :param device_event_handler: Event handler for this example.
    :type cam: CameraPtr
    :type device_event_handler: DeviceEventHandler
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Unregister device event
        #
        # *** NOTES ***
        # It is important to unregister all device events from all cameras that
        # they are registered to.
        cam.UnregisterEvent(device_event_handler)

        print "Device event handler unregistered...\n"

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
     :return: True if successful, False otherwise.
     :rtype: bool
    """
    print "\n*** DEVICE INFORMATION ***\n"

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
        print "Error: %s" % ex.message
        return False

    return result


def acquire_images(cam, nodemap, nodemap_tldevice):
    """
    This function acquires and saves 10 images from a device; please see
    Acquisition example for more in-depth comments on acquiring images.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print "\n*** IMAGE ACQUISITION ***\n"
    try:
        result = True

        # Set acquisition mode to continuous
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print "Unable to set acquisition mode to continuous (enum retrieval). Aborting...\n"
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) \
                or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print "Unable to set acquisition mode to continuous (entry retrieval). Aborting...\n"
            return False

        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print "Acquisition mode set to continuous..."

        #  Begin acquiring images
        cam.BeginAcquisition()

        print "Acquiring images..."

        # Retrieve device serial number for filename
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceSerialNumber"))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print "Device serial number retrieved as %s..." % device_serial_number

        # Retrieve, convert, and save images
        for i in range(NUM_IMAGES):
            try:
                # Retrieve next received image and ensure image completion
                image_result = cam.GetNextImage()

                if image_result.IsIncomplete():
                    print "Image incomplete with image status %s..." % image_result.GetImageStatus()

                else:

                    # Print image information
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    print "Grabbed Image %i, width = %i, height = %i" % (i, width, height)

                    # Convert to mono8
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                    if device_serial_number:
                        filename = "DeviceEvents-%s-%i.jpg" % (device_serial_number, i)
                    else:
                        filename = "DeviceEvents-%i.jpg" % i

                    # Save image
                    image_converted.Save(filename)
                    print "Image saved at %s" % filename

                # Release image
                image_result.Release()
                print ""

            except PySpin.SpinnakerException as ex:
                print "Error: %s" % ex
                result = False

        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

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

        # Configure device events
        err, device_event_handler = configure_device_events(nodemap, cam)
        if not err:
            return err

        # Acquire images
        result &= acquire_images(cam, nodemap, nodemap_tldevice)

        # Reset device events
        result &= reset_device_events(cam, device_event_handler)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex.message
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
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

        result = run_single_camera(cam)
        print "Camera %d example complete..." % i

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release instance
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")
    return result

if __name__ == "__main__":
    main()
