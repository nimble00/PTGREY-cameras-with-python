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
# NodeMapInfo.py shows how to retrieve node map information. It relies
# on information provided in the Enumeration example. Also, check out the
# Acquisition and ExceptionHandling examples if you haven't already.
# Acquisition demonstrates image acquisition while ExceptionHandling shows the
# handling of standard and Spinnaker exceptions.
#
# This example explores retrieving information from all major node types on the
# camera. This includes string, integer, float, boolean, command, enumeration,
# category, and value types. Looping through multiple child nodes is also
# covered. A few node types are not covered - base, port, and register - as
# they are not fundamental. The final node type - enumeration entry - is
# explored only in terms of its parent node type - enumeration.
#
# Once comfortable with NodeMapInfo, we suggest checking out ImageFormatControl
# and Exposure. ImageFormatControl explores customizing image settings on a
# camera while Exposure introduces the standard structure of configuring a
# device, acquiring some images, and then returning the device to a default
# state.
import pyspin
from pyspin import PySpin

# Defines max number of characters that will be printed out for any node information
MAX_CHARS = 35


class ReadType:
    """
    Use the following constants to determine whether nodes are read
    as Value nodes or their individual types.
    """
    VALUE = 0,
    INDIVIDUAL = 1

CHOSEN_READ = ReadType.INDIVIDUAL


def print_with_indent(level, text):
    """
    Helper function for printing a string prefix with a specifc number of indents.
    :param level: Number of indents to generate
    :type level: int
    :param text: String to print after indent
    :type text: str
    """
    ind = ''
    for i in range(level):
        ind += '    '
    print "%s%s" % (ind, text)


def print_value_node(node, level):
    """
    Retrieves and prints the display name and value of all node types as value nodes.
    A value node is a general node type that allows for the reading and writing of any node type as a string.

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create value node
        node_value = PySpin.CValuePtr(node)

        # Retrieve display name
        #
        # *** NOTES ***
        # A node's 'display name' is generally more appropriate for output and
        # user interaction whereas its 'name' is what the camera understands.
        # Generally, its name is the same as its display name but without
        # spaces - for instance, the name of the node that houses a camera's
        # serial number is 'DeviceSerialNumber' while its display name is
        # 'Device Serial Number'.
        display_name = node_value.GetDisplayName()

        # Retrieve value of any node type as string
        #
        # *** NOTES ***
        # Because value nodes return any node type as a string, it can be much
        # easier to deal with nodes as value nodes rather than their actual
        # individual types.
        value = node_value.ToString()

        # Cap length at MAX_CHARS
        value = value[:MAX_CHARS] + '...' if len(value) > MAX_CHARS else value

        # Print value
        print_with_indent(level, "%s: %s" % (display_name, value))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_string_node(node, level):
    """
    Retrieves and prints the display name and value of a string node.

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create string node
        node_string = PySpin.CStringPtr(node)

        # Retrieve string node value
        #
        # *** NOTES ***
        # Functions in Spinnaker C++ that use gcstring types
        # are substituted with Python strings in PySpin.
        # The only exception is shown in the DeviceEvents example, where
        # the callback function still uses a wrapped gcstring type.
        display_name = node_string.GetDisplayName()

        # Ensure that the value length is not excessive for printing
        value = node_string.GetValue()
        value = value[:MAX_CHARS] + '...' if len(value) > MAX_CHARS else value

        # Print value; 'level' determines the indentation level of output
        print_with_indent(level, "%s: %s" % (display_name, value))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_integer_node(node, level):
    """
    Retrieves and prints the display name and value of an integer node.

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create integer node
        node_integer = PySpin.CIntegerPtr(node)

        # Get display name
        display_name = node_integer.GetDisplayName()

        # Retrieve integer node value
        #
        # *** NOTES ***
        # All node types except base nodes have a ToString()
        # method which returns a value as a string.
        value = node_integer.GetValue()

        # Print value
        print_with_indent(level, "%s: %s" % (display_name, value))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_float_node(node, level):
    """
    Retrieves and prints the display name and value of a float node.

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create float node
        node_float = PySpin.CFloatPtr(node)

        # Get display name
        display_name = node_float.GetDisplayName()

        # Retrieve float value
        value = node_float.GetValue()

        # Print value
        print_with_indent(level, "%s: %s" % (display_name, value))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_boolean_node(node, level):
    """
    Retrieves and prints the display name and value of a Boolean node.

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create Boolean node
        node_boolean = PySpin.CBooleanPtr(node)

        # Get display name
        display_name = node_boolean.GetDisplayName()

        # Retrieve Boolean value
        value = node_boolean.GetValue()

        # Print Boolean value
        # NOTE: In Python a Boolean will be printed as "True" or "False".
        print_with_indent(level, "%s: %s" % (display_name, value))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_command_node(node, level):
    """
    This function retrieves and prints the display name and tooltip of a command
    node, limiting the number of printed characters to a macro-defined maximum.
    The tooltip is printed below because command nodes do not have an intelligible
    value.

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create command node
        node_command = PySpin.CCommandPtr(node)

        # Get display name
        display_name = node_command.GetDisplayName()

        # Retrieve tooltip
        #
        # *** NOTES ***
        # All node types have a tooltip available. Tooltips provide useful
        # information about nodes. Command nodes do not have a method to
        # retrieve values as their is no intelligible value to retrieve.
        tooltip = node_command.GetToolTip()

        # Ensure that the value length is not excessive for printing
        tooltip = tooltip[:MAX_CHARS] + '...' if len(tooltip) > MAX_CHARS else tooltip

        # Print display name and tooltip
        print_with_indent(level, "%s: %s" % (display_name, tooltip))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_enumeration_node_and_current_entry(node, level):
    """
    This function retrieves and prints the display names of an enumeration node
    and its current entry (which is actually housed in another node unto itself).

    :param node: Node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create enumeration node
        node_enumeration = PySpin.CEnumerationPtr(node)

        # Retrieve current entry as enumeration node
        #
        # *** NOTES ***
        # Enumeration nodes have three methods to differentiate between: first,
        # GetIntValue() returns the integer value of the current entry node;
        # second, GetCurrentEntry() returns the entry node itself; and third,
        # ToString() returns the symbolic of the current entry.
        node_enum_entry = PySpin.CEnumEntryPtr(node_enumeration.GetCurrentEntry())

        # Get display name
        display_name = node_enumeration.GetDisplayName()

        # Retrieve current symbolic
        #
        # *** NOTES ***
        # Rather than retrieving the current entry node and then retrieving its
        # symbolic, this could have been taken care of in one step by using the
        # enumeration node's ToString() method.
        entry_symbolic = node_enum_entry.GetSymbolic()

        # Print current entry symbolic
        print_with_indent(level, "%s: %s" % (display_name, entry_symbolic))

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def print_category_node_and_all_features(node, level):
    """
    This function retrieves and prints out the display name of a category node
    before printing all child nodes. Child nodes that are also category nodes are
    printed recursively.

    :param node: Category node to get information from.
    :type node: INode
    :param level: Depth to indent output.
    :type level: int
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Create category node
        node_category = PySpin.CCategoryPtr(node)

        # Get and print display name
        display_name = node_category.GetDisplayName()
        print_with_indent(level, display_name)

        # Retrieve and iterate through all children
        #
        # *** NOTES ***
        # The two nodes that typically have children are category nodes and
        # enumeration nodes. Throughout the examples, the children of category nodes
        # are referred to as features while the children of enumeration nodes are
        # referred to as entries. Keep in mind that enumeration nodes can be cast as
        # category nodes, but category nodes cannot be cast as enumerations.
        for node_feature in node_category.GetFeatures():

            # Ensure node is available and readable
            if not PySpin.IsAvailable(node_feature) or not PySpin.IsReadable(node_feature):
                continue

            # Category nodes must be dealt with separately in order to retrieve subnodes recursively.
            if node_feature.GetPrincipalInterfaceType() == PySpin.intfICategory:
                result &= print_category_node_and_all_features(node_feature, level + 1)

            # Cast all non-category nodes as value nodes
            #
            # *** NOTES ***
            # If dealing with a variety of node types and their values, it may be
            # simpler to cast them as value nodes rather than as their individual types.
            # However, with this increased ease-of-use, functionality is sacrificed.
            elif CHOSEN_READ == ReadType.VALUE:
                result &= print_value_node(node_feature, level + 1)

            # Cast all non-category nodes as actual types
            elif CHOSEN_READ == ReadType.INDIVIDUAL:
                if node_feature.GetPrincipalInterfaceType() == PySpin.intfIString:
                    result &= print_string_node(node_feature, level + 1)
                elif node_feature.GetPrincipalInterfaceType() == PySpin.intfIInteger:
                    result &= print_integer_node(node_feature, level + 1)
                elif node_feature.GetPrincipalInterfaceType() == PySpin.intfIFloat:
                    result &= print_float_node(node_feature, level + 1)
                elif node_feature.GetPrincipalInterfaceType() == PySpin.intfIBoolean:
                    result &= print_boolean_node(node_feature, level + 1)
                elif node_feature.GetPrincipalInterfaceType() == PySpin.intfICommand:
                    result &= print_command_node(node_feature, level + 1)
                elif node_feature.GetPrincipalInterfaceType() == PySpin.intfIEnumeration:
                    result &= print_enumeration_node_and_current_entry(node_feature, level + 1)

        print ""

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return result


def run_single_camera(cam):
    """
    This function acts as the body of the example. First nodes from the TL
    device and TL stream nodemaps are retrieved and printed. Following this,
    the camera is initialized and then nodes from the GenICam nodemap are
    retrieved and printed.

    :param cam: Camera to get nodemaps from.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True
        level = 0

        # Retrieve TL device nodemap
        #
        # *** NOTES ***
        # The TL device nodemap is available on the transport layer. As such,
        # camera initialization is unnecessary. It provides mostly immutable
        # information fundamental to the camera such as the serial number,
        # vendor, and model.
        print "\n*** PRINTING TRANSPORT LAYER DEVICE NODEMAP *** \n"

        nodemap_gentl = cam.GetTLDeviceNodeMap()

        result &= print_category_node_and_all_features(nodemap_gentl.GetNode('Root'), level)

        # Retrieve TL stream nodemap
        #
        # *** NOTES ***
        # The TL stream nodemap is also available on the transport layer. Camera
        # initialization is again unnecessary. As you can probably guess, it
        # provides information on the camera's streaming performance at any
        # given moment. Having this information available on the transport layer
        # allows the information to be retrieved without affecting camera performance.
        print "*** PRINTING TL STREAM NODEMAP ***\n"

        nodemap_tlstream = cam.GetTLStreamNodeMap()

        result &= print_category_node_and_all_features(nodemap_tlstream.GetNode('Root'), level)

        # Initialize camera
        #
        # *** NOTES ***
        # The camera becomes connected upon initialization. This provides
        # access to configurable options and additional information, accessible
        # through the GenICam nodemap.
        #
        # *** LATER ***
        # Cameras should be deinitialized when no longer needed.
        print "*** PRINTING GENICAM NODEMAP ***\n"

        cam.Init()

        # Retrieve GenICam nodemap
        #
        # *** NOTES ***
        # The GenICam nodemap is the primary gateway to customizing
        # and configuring the camera to suit your needs. Configuration options
        # such as image height and width, trigger mode enabling and disabling,
        # and the sequencer are found on this nodemap.
        nodemap_applayer = cam.GetNodeMap()

        result &= print_category_node_and_all_features(nodemap_applayer.GetNode('Root'), level)

        # Deinitialize camera
        #
        # *** NOTES ***
        # Camera deinitialization helps ensure that devices clean up properly
        # and do not need to be power-cycled to maintain integrity.
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print "Error: %s" % ex
        return False

    return True


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
