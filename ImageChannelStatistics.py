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
# ImageChannelStatisitcs.py shows how to get the image data and channel statistics, and then saves / displays them.
# This example relies on information provided in the Acquisition examples.
#
# This example demonstrates how to visualize the image histogram using Python, and display an image represented as
# a numpy array.

import PySpin
import matplotlib.pyplot as plt

NUM_IMAGES = 10  # number of images to grab


def acquire_and_display_images(cam, nodemap, nodemap_tldevice):
    """
    This function acquires and displays the channel statistics of N images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print "*** IMAGE ACQUISITION ***\n"
    try:
        result = True

        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print "Unable to set acquisition mode to continuous (enum retrieval). Aborting..."
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName("Continuous")
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print "Unable to set acquisition mode to continuous (entry retrieval). Aborting..."
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print "Acquisition mode set to continuous..."

        node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
        if not PySpin.IsAvailable(node_pixel_format) or not PySpin.IsWritable(node_pixel_format):
            print "Unable to set Pixel Format. Aborting..."
            return False

        else:
            # Retrieve entry node from enumeration node
            node_pixel_format_mono8 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName("Mono8"))
            if not PySpin.IsAvailable(node_pixel_format_mono8) or not PySpin.IsReadable(node_pixel_format_mono8):
                print "Unable to set Pixel Format to MONO8. Aborting..."
                return False

            # Retrieve integer value from entry node
            pixel_format_mono8 = node_pixel_format_mono8.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_pixel_format.SetIntValue(pixel_format_mono8)

            print "Pixel Format set to MONO8 ..."

        cam.BeginAcquisition()

        print "Acquiring images..."

        device_serial_number = ""
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceSerialNumber"))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print "Device serial number retrieved as %s..." % device_serial_number

        plt.ion()
        for i in range(NUM_IMAGES):
            try:
                image_result = cam.GetNextImage()

                if image_result.IsIncomplete():
                    print "Image incomplete with image status %d ..." % image_result.GetImageStatus()
                else:
                    fig = plt.figure(1)

                try:
                    image_stats = image_result.CalculateChannelStatistics(PySpin.GREY)
                    # Getting the image data as a numpy array
                    image_data = image_result.GetNDArray()

                    # Display Statistics
                    print "SN%s image %d:" % (device_serial_number, i)
                    print "\tNumber pixel values : %d" % image_stats.num_pixel_values
                    print "\tRange:                Min = %d, Max = %d" % (image_stats.range_min,
                                                                          image_stats.range_max)
                    print "\tPixel Value:          Min = %d, Max = %d, Mean = %.2f" % (image_stats.pixel_value_min,
                                                                                       image_stats.pixel_value_max,
                                                                                       image_stats.pixel_value_mean)

                    # Using matplotlib, two subplots are created where the top subplot is the histogram and the 
                    # bottom subplot is the image.
                    # 
                    # Refer to https://matplotlib.org/2.0.2/api/pyplot_api.html#module-matplotlib.pyplot
                                                                                       
                    # Plot the histogram in the first subplot in a 2 row by 1 column grid
                    plt.subplot(211)
                    plt.cla()
                    plt.plot(image_stats.histogram, label='Grey')
                    plt.title("SN%s Histogram (%d)" % (device_serial_number, i))
                    plt.legend()

                    # Plot the image in the second subplot in a 2 row by 1 column grid
                    plt.subplot(212)
                    plt.cla()
                    plt.imshow(image_data, cmap='gray')

                    # Show the image
                    plt.show()
                    plt.pause(0.01)

                    # Create a unique filename
                    if device_serial_number:
                        filename = "ImageChannelStatistics-%s-%d.png" % (device_serial_number, i)
                    else:  # if serial number is empty
                        filename = "ImageChannelStatistics-%d.png" % i

                    fig.savefig(filename)
                    print "\tSave to %s" % filename
                    print

                except PySpin.SpinnakerException:
                    raise

                #  Release image
                #
                #  *** NOTES ***
                #  Images retrieved directly from the camera (i.e. non-converted
                #  images) need to be released in order to keep from filling the
                #  buffer.
                image_result.Release()

            except PySpin.SpinnakerException:
                raise

        cam.EndAcquisition()
        print "End Acquisition"

        plt.close()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        #Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_and_display_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result

def main():
    """
    Example entry point; notice the volume of data that the logging event handler
    prints out on debug despite the fact that very little really happens in this
    example. Because of this, it may be better to have the logger set to lower
    level in order to provide a more concise, focused log.

    :rtype: None
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

