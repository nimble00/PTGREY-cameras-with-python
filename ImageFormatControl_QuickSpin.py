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
# ImageFormatControl_QuickSpin.py shows how to apply custom image
# settings to the camera using the QuickSpin API. QuickSpin is a subset of
# the Spinnaker library that allows for simpler node access and control.
#
# This example demonstrates customizing offsets X and Y, width and height,
# and the pixel format. Ensuring custom values fall within an acceptable
# range is also touched on. Retrieving and setting node values using
# QuickSpin is the only portion of the example that differs from
# ImageFormatControl.
#
# A much wider range of topics is covered in the full Spinnaker examples than
# in the QuickSpin ones. There are only enough QuickSpin examples to
# demonstrate node access and to get started with the API; please see full
# Spinnaker examples for further or specific knowledge on a topic.

import PySpin

NUM_IMAGES = 10  # number of images to grab


def configure_custom_image_settings(cam):
    """
    Configures a number of settings on the camera including offsets X and Y,
    width, height, and pixel format. These settings must be applied before
    BeginAcquisition() is called; otherwise, those nodes would be read only.
    Also, it is important to note that settings are applied immediately.
    This means if you plan to reduce the width and move the x offset accordingly,
    you need to apply such changes in the appropriate order.

    :param cam: Camera to configure settings on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print "\n*** CONFIGURING CUSTOM IMAGE SETTINGS ***\n"

    try:
        result = True

        # Apply mono 8 pixel format
        #
        # *** NOTES ***
        # In QuickSpin, enumeration nodes are as easy to set as other node
        # types. This is because enum values representing each entry node
        # are added to the API.
        if cam.PixelFormat.GetAccessMode() == PySpin.RW:
            cam.PixelFormat.SetValue(PySpin.PixelFormat_Mono8)
            print "Pixel format set to %s..." % cam.PixelFormat.GetCurrentEntry().GetSymbolic()

        else:
            print "Pixel format not available..."
            result = False
            
        # Apply minimum to offset X
        #
        # *** NOTES ***
        # Numeric nodes have both a minimum and maximum. A minimum is retrieved
        # with the method GetMin(). Sometimes it can be important to check
        # minimums to ensure that your desired value is within range.
        if cam.OffsetX.GetAccessMode() == PySpin.RW:
            cam.OffsetX.SetValue(cam.OffsetX.GetMin())
            print "Offset X set to %d..." % cam.OffsetX.GetValue()

        else:
            print "Offset X not available..."
            result = False

        # Apply minimum to offset Y
        #
        # *** NOTES ***
        # It is often desirable to check the increment as well. The increment
        # is a number of which a desired value must be a multiple. Certain
        # nodes, such as those corresponding to offsets X and Y, have an
        # increment of 1, which basically means that any value within range
        # is appropriate. The increment is retrieved with the method GetInc().
        if cam.OffsetY.GetAccessMode() == PySpin.RW:
            cam.OffsetY.SetValue(cam.OffsetY.GetMin())
            print "Offset Y set to %d..." % cam.OffsetY.GetValue()

        else:
            print "Offset Y not available..."
            result = False

        # Set maximum width
        #
        # *** NOTES ***
        # Other nodes, such as those corresponding to image width and height,
        # might have an increment other than 1. In these cases, it can be
        # important to check that the desired value is a multiple of the
        # increment.
        #
        # This is often the case for width and height nodes. However, because
        # these nodes are being set to their maximums, there is no real reason
        # to check against the increment.
        if cam.Width.GetAccessMode() == PySpin.RW and cam.Width.GetInc() != 0 and cam.Width.GetMax != 0:
            cam.Width.SetValue(cam.Width.GetMax())
            print "Width set to %i..." % cam.Width.GetValue()

        else:
            print "Width not available..."
            result = False

        # Set maximum height
        #
        # *** NOTES ***
        # A maximum is retrieved with the method GetMax(). A node's minimum and
        # maximum should always be a multiple of its increment.
        if cam.Height.GetAccessMode() == PySpin.RW and cam.Height.GetInc() != 0 and cam.Height.GetMax != 0:
            cam.Height.SetValue(cam.Height.GetMax())
            print "Height set to %i..." % cam.Height.GetValue()

        else:
            print "Height not available..."
            result = False

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_device_info(cam):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param cam: Camera to get device information from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print "\n*** DEVICE INFORMATION ***\n"

    try:
        result = True
        nodemap = cam.GetTLDeviceNodeMap()

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


def acquire_images(cam):
    """
    This function acquires and saves 10 images from a device; please see
    Acquisition example for more in-depth comments on the acquisition of images.

    :param cam: Camera to acquire images from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    print "\n*** IMAGE ACQUISITION ***\n"

    try:
        result = True

        # Set acquisition mode to continuous
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            print "Unable to set acquisition mode to continuous. Aborting..."
            return False

        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        print "Acquisition mode set to continuous..."

        # Begin acquiring images
        cam.BeginAcquisition()

        print "Acquiring images..."

        # Get device serial number for filename
        device_serial_number = ""
        if cam.TLDevice.DeviceSerialNumber is not None and cam.TLDevice.DeviceSerialNumber.GetAccessMode() == PySpin.RO:
            device_serial_number = cam.TLDevice.DeviceSerialNumber.GetValue()

            print "Device serial number retrieved as %s..." % device_serial_number

        # Retrieve, convert, and save images
        for i in range(NUM_IMAGES):

            try:
                # Retrieve next received image and ensure image completion
                image_result = cam.GetNextImage()

                if image_result.IsIncomplete():
                    print "Image incomplete with image status %d..." % image_result.GetImageStatus()

                else:
                    # Print image information
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    print "Grabbed Image %d, width = %d, height = %d" % (i, width, height)

                    # Convert image to Mono8
                    image_converted = image_result.Convert(PySpin.PixelFormat_Mono8)

                    # Create a unique filename
                    if device_serial_number:
                        filename = "ImageFormatControlQS-%s-%d.jpg" % (device_serial_number, i)
                    else:
                        filename = "ImageFormatControlQS-%d.jpg" % i

                    # Save image
                    image_converted.Save(filename)

                    print "Image saved at %s" % filename

                # Release image
                image_result.Release()

            except PySpin.SpinnakerException as ex:
                print "Error: %s" % ex
                result = False

        # End acquisition
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def run_single_camera(cam):
    """
     This function acts as the body of the example; please see NodeMapInfo_QuickSpin example for more
     in-depth comments on setting up cameras.

     :param cam: Camera to run example on.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """
    try:
        # Initialize camera
        cam.Init()

        # Print device info
        result = print_device_info(cam)

        # Configure exposure
        if not configure_custom_image_settings(cam):
            return False

        # Acquire images
        result &= acquire_images(cam)

        # Deinitialize camera
        cam.DeInit()

        return result

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False


def main():
    """
    Example entry point; please see Enumeration_QuickSpin example for more
    in-depth comments on preparing and cleaning up the system.

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

    # Release example on each camera
    for i in range(num_cameras):
        print "Running example for camera %d..." % i

        result = run_single_camera(cam_list.GetByIndex(i))

        print "Camera %d example complete..." % i

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")
    return result

if __name__ == "__main__":
    main()
