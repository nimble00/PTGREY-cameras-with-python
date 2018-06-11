# coding=utf-8
# =============================================================================
# Copyright © 2017 FLIR Integrated Imaging Solutions, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# SpinUpdate.py is a sample firmware updater application that takes in
# command line arguments. The example also demonstrates usage of callback
# functions to keep track of current update progress.
#
# Run with arguments in format (no quotes): "-R<serial number> -P -UU <path to firmware file>"

import PySpin
import sys


last_action = ""


def progress_callback(action, address, global_percent, curr_percent):
    """
    Example progress callback function.
    NOTE: This function must take exactly 4 arguments,
    otherwise the update process will hang/crash!

    :param action: Current action being done in firmware update.
    :param address: Address in camera being written to.
    :param global_percent: Global completion percentage of update.
    :param curr_percent: Completion percentage of current action.
    :type action: str
    :type address: int
    :type global_percent: int
    :type curr_percent: int
    :rtype: int
    """
    global last_action
    if action != last_action:
        # Prints action only if changed from previous one
        print "Action: %s" % action
        last_action = action

    return 1


def message_callback(message):
    """
    Example message callback function.
    NOTE: This function must take exactly 1 argument,
    otherwise the update process will hang/crash!

    :param message: Message from updator.
    :type message: str
    :rtype: None
    """
    print "Message: %s" % message


def main():
    # Register callbacks
    PySpin.SetProgressCallback(progress_callback)
    PySpin.SetMessageCallback(message_callback)

    # Example usage for firmware update:
    # Use either UpdateFirmware() or UpdateFirmwareConsole():
    #
    # cmd = "-R3932019 C:\\firmware\\bfly2_u3_python1300.zim" # Add -P to argument list for callbacks
    # return UpdateFirmware(cmd);

    return PySpin.UpdateFirmwareConsole(sys.argv)  # uses command line args

if __name__ == '__main__':
    main()
