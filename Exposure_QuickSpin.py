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
#  Exposure_QuickSpin.py shows how to customize image exposure time
#  using the QuickSpin API. QuickSpin is a subset of the Spinnaker library
#  that allows for simpler node access and control.
#
#  This example prepares the camera, sets a new exposure time, and restores
#  the camera to its default state. Ensuring custom values fall within an
#  acceptable range is also touched on. Retrieving and setting information
#  is the only portion of the example that differs from Exposure.
#
#  A much wider range of topics is covered in the full Spinnaker examples than
#  in the QuickSpin ones. There are only enough QuickSpin examples to
#  demonstrate node access and to get started with the API; please see full
#  Spinnaker examples for further or specific knowledge on a topic.

import PySpin

NUM_IMAGES = 5  # number of images to save


def configure_exposure(cam):
    """
     This function configures a custom exposure time. Automatic exposure is turned
     off in order to allow for the customization, and then the custom setting is
     applied.

     :param cam: Camera to configure exposure for.
     :type cam: CameraPtr
     :return: True if successful, False otherwise.
     :rtype: bool
    """

    print "*** CONFIGURING EXPOSURE ***\n"

    try:
        result = True

        # Turn off automatic exposure mode
        #
        # *** NOTES ***
        # Automatic exposure prevents the manual configuration of exposure
        # times and needs to be turned off for this example. Enumerations
        # representing entry nodes have been added to QuickSpin. This allows
        # for the much easier setting of enumeration nodes to new values.
        #
        # The naming convention of QuickSpin enums is the name of the
        # enumeration node followed by an underscore and the symbolic of
        # the entry node. Selecting "Off" on the "ExposureAuto" node is
        # thus named "ExposureAuto_Off".
        #
        # *** LATER ***
        # Exposure time can be set automatically or manually as needed. This
        # example turns automatic exposure off to set it manually and back
        # on to return the camera to its default state.

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print "Unable to disable automatic exposure. Aborting..."
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        print "Automatic exposure disabled..."

        # Set exposure time manually; exposure time recorded in microseconds
        #
        # *** NOTES ***
        # Notice that the node is checked for availability and writability
        # prior to the setting of the node. In QuickSpin, availability and
        # writability are ensured by checking the access mode.
        #
        # Further, it is ensured that the desired exposure time does not exceed
        # the maximum. Exposure time is counted in microseconds - this can be
        # found out either by retrieving the unit with the GetUnit() method or
        # by checking SpinView.

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            print "Unable to set exposure time. Aborting..."
            return False

        # Ensure desired exposure time does not exceed the maximum
        exposure_time_to_set = 2000000.0
        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

    return result


def reset_exposure(cam):
    """
    This function returns the camera to a normal state by re-enabling automatic exposure.

    :param cam: Camera to reset exposure on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Turn automatic exposure back on
        #
        # *** NOTES ***
        # Automatic exposure is turned on in order to return the camera to its
        # default state.

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            print "Unable to enable automatic exposure (node retrieval). Non-fatal error..."
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

        print "Automatic exposure enabled..."

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        result = False

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

    print "*** DEVICE INFORMATION ***\n"

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
    print "*** IMAGE ACQUISITION ***"

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
                    filename = "ExposureQS-%s-%d.jpg" % (device_serial_number, i)

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
        if not configure_exposure(cam):
            return False

        # Acquire images
        result &= acquire_images(cam)

        # Reset exposure
        result &= reset_exposure(cam)

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
