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
#   ImageEvents.py shows how to acquire images using the image event handler.
#   It relies on information provided in the Enumeration, Acquisition,
#  	and NodeMapInfo examples.
#
#  	It can also be helpful to familiarize yourself with the NodeMapCallback
#  	example, as nodemap callbacks follow the same general procedure as
#  	events, but with a few less steps.
#
#  	This example creates a user-defined class, ImageEventHandler, that inherits
#  	from the Spinnaker class, ImageEvent. ImageEventHandler allows the user to
#  	define any properties, parameters, and the event itself while ImageEvent
#  	allows the child class to appropriately interface with Spinnaker.


import PySpin
from time import sleep

SLEEP_DURATION = 200  # amount of time for main thread to sleep for (in milliseconds) until _NUM_IMAGES have been saved


class ImageEventHandler(PySpin.ImageEvent):
    """
    This class defines the properties, parameters, and the event itself. Take a
    moment to notice what parts of the class are mandatory, and what have been
    added for demonstration purposes. First, any class used to define image events
    must inherit from ImageEvent. Second, the method signature of OnImageEvent()
    must also be consistent. Everything else - including the constructor,
    destructor, properties, body of OnImageEvent(), and other functions -
    is particular to the example.
    """
    _NUM_IMAGES = 10

    def __init__(self, cam):
        """
        Constructor. Retrieves serial number of given camera and sets image counter to 0.

        :param cam: Camera instance, used to get serial number for unique image filenames.
        :type cam: CameraPtr
        :rtype: None
        """
        super(ImageEventHandler, self).__init__()

        nodemap = cam.GetTLDeviceNodeMap()

        # Retrieve device serial number
        node_device_serial_number = PySpin.CStringPtr(nodemap.GetNode("DeviceSerialNumber"))

        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            self._device_serial_number = node_device_serial_number.GetValue()

        # Initialize image counter to 0
        self._image_count = 0

        # Release reference to camera
        del cam

    def OnImageEvent(self, image):
        """
        This method defines an image event. In it, the image that triggered the
        event is converted and saved before incrementing the count. Please see
        Acquisition example for more in-depth comments on the acquisition
        of images.

        :param image: Image from event.
        :type image: ImagePtr
        :rtype: None
        """
        # Save max of _NUM_IMAGES Images
        if self._image_count < self._NUM_IMAGES:
            print "Image event occurred..."

            # Check if image is incomplete
            if image.IsIncomplete():
                print "Image incomplete with image status %i..." % image.GetImageStatus()

            else:
                # Print image info
                print "Grabbed image %i, width = %i, height = %i" % (self._image_count,
                                                                     image.GetWidth(),
                                                                     image.GetHeight())

                # Convert to mono8
                image_converted = image.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                # Create unique filename and save image
                if self._device_serial_number:
                    filename = "ImageEvents-%s-%i.jpg" % (self._device_serial_number, self._image_count)

                else:  # if serial number is empty
                    filename = "ImageEvents-%i.jpg" % self._image_count

                image_converted.Save(filename)

                print "Image saved at %s\n" % filename

                # Increment image counter
                self._image_count += 1

    def get_image_count(self):
        """
        Getter for image count.

        :return: Number of images saved.
        :rtype: int
        """
        return self._image_count

    def get_max_images(self):
        """
        Getter for maximum images.

        :return: Total number of images to save.
        :rtype: int
        """
        return self._NUM_IMAGES


def configure_image_events(cam):
    """
    This function configures the example to execute image events by preparing and
    registering an image event.

    :param cam: Camera instance to configure image event.
    :return: tuple(result, image_event_handler)
        WHERE
        result is True if successful, False otherwise
        image_event_handler is the event handler
    :rtype: (bool, ImageEventHandler)
    """
    try:
        result = True

        #  Create image event
        #
        #  *** NOTES ***
        #  The class has been constructed to accept a camera pointer in order
        #  to allow the saving of images with the device serial number.
        image_event_handler = ImageEventHandler(cam)

        #  Register image event handler
        #
        #  *** NOTES ***
        #  Image events are registered to cameras. If there are multiple
        #  cameras, each camera must have the image events registered to it
        #  separately. Also, multiple image events may be registered to a
        #  single camera.
        #
        #  *** LATER ***
        #  Image events must be unregistered manually. This must be done prior
        #  to releasing the system and while the image events are still in
        #  scope.
        cam.RegisterEvent(image_event_handler)

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result, image_event_handler


def wait_for_images(image_event_handler):
    """
    This function waits for the appropriate amount of images.  Notice that
    whereas most examples actively retrieve images, the acquisition of images is
    handled passively in this example.

    :param image_event_handler: Image event handler.
    :type image_event_handler: ImageEventHandler
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        #  Wait for images
        #
        #  *** NOTES ***
        #  In order to passively capture images using image events and
        #  automatic polling, the main thread sleeps in increments of SLEEP_DURATION ms
        #  until _MAX_IMAGES images have been acquired and saved.
        while image_event_handler.get_image_count() < image_event_handler.get_max_images():
            print "\t//\n\t// Sleeping for %i ms. Grabbing images..." % SLEEP_DURATION
            sleep(SLEEP_DURATION / 1000.0)

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def reset_image_events(cam, image_event_handler):
    """
    This functions resets the example by unregistering the image event.

    :param cam: Camera instance.
    :param image_event_handler: Image event handler for cam.
    :type cam: CameraPtr
    :type image_event_handler: ImageEventHandler
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        #  Unregister image event handler
        #
        #  *** NOTES ***
        #  It is important to unregister all image events from all cameras they are registered to.
        #  Unlike SystemEventHandler and InterfaceEventHandler in the EnumerationEvents example,
        #  there is no need to explicitly delete the ImageEventHandler here as it does not store
        #  an instance of the camera (it gets deleted in the constructor already).
        cam.UnregisterEvent(image_event_handler)

        print "Image events unregistered..."

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap from camera.
    :type nodemap: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print "*** DEVICE INFORMATION ***"

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
        result = False

    return result


def acquire_images(cam, nodemap, image_event_handler):
    """
    This function passively waits for images by calling wait_for_images(). Notice that
    this function is much shorter than the acquire_images() function of other examples.
    This is because most of the code has been moved to the image event's OnImageEvent()
    method.

    :param cam: Camera instance to grab images from.
    :param nodemap: Device nodemap.
    :param image_event_handler: Image event handler.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type image_event_handler: ImageEventHandler
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print "*** IMAGE ACQUISITION ***\n"
    try:
        result = True

        # Set acquisition mode to continuous
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print "Unable to set acquisition mode to continuous (enum retrieval). Aborting..."
            return False

        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            print "Unable to set acquisition mode to continuous (entry retrieval). Aborting..."
            return False

        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print "Acquisition mode set to continuous..."

        # Begin acquiring images
        cam.BeginAcquisition()

        print "Acquiring images..."

        # Retrieve images using image event handler
        wait_for_images(image_event_handler)

        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example 
    for more in-depth comments on setting up cameras.

    :param cam: Camera to acquire images from.
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

        # Configure image events
        err, image_event_handler = configure_image_events(cam)
        if not err:
            return err

        # Acquire images using the image event handler
        result &= acquire_images(cam, nodemap, image_event_handler)

        # Reset image events
        result &= reset_image_events(cam, image_event_handler)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for additional 
    comments on the steps in this function.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()
    
    num_cams = cam_list.GetSize()

    print "Number of cameras detected: %i" % num_cams

    # Finish if there are no cameras
    if num_cams == 0:
        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system
        system.ReleaseInstance()

        print "Not enough cameras!"
        raw_input("Done! Press Enter to exit...")

    # Run example on each camera
    for i in range(num_cams):
        print "Running example for camera %i..." % i

        result &= run_single_camera(cam_list.GetByIndex(i))

        print "Camera %i example complete..." % i

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system
    system.ReleaseInstance()
    raw_input("Done! Press Enter to exit...")

    return result

if __name__ == "__main__":
    main()
