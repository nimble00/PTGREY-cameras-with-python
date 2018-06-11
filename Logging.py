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
#  	Logging.py shows how to create a handler to access logging events.
#  	It relies on information provided in the Enumeration, Acquisition, and
#  	NodeMapInfo examples.
#
#  	It can also be helpful to familiarize yourself with the NodeMapCallback
#  	example, as nodemap callbacks follow the same general procedure as
#  	events, but with a few less steps.
#
#  	This example creates a user-defined class, LoggingEventHandler, that inherits
#  	from the Spinnaker class, LoggingEvent. The child class allows the user to
#  	define any properties, parameters, and the event itself while LoggingEvent
#  	allows the child class to appropriately interface with the Spinnaker SDK.

import PySpin


# Define callback priority threshold; please see documentation for additional
# information on logging level philosophy.
LOGGING_LEVEL = PySpin.LOG_LEVEL_DEBUG  # change to any LOG_LEVEL_* constant


class LoggingEventHandler(PySpin.LoggingEvent):
    """
    Although logging events are just as flexible and extensible as other events,
    they are generally only used for logging purposes, which is why a number of
    helpful functions that provide logging information have been added. Generally,
    if the purpose is not logging, one of the other event types is probably more
    appropriate.
    """

    def __init__(self):
        super(LoggingEventHandler, self).__init__()

    def OnLogEvent(self, logging_event_data):
        """
        This function displays readily available logging information.

        :param logging_event_data: Logging data.
        :type logging_event_data: LoggingEventData
        :rtype: None
        """
        print "--------Log Event Received----------"
        print "Category: %s" % logging_event_data.GetCategoryName()
        print "Priority Value: %s" % logging_event_data.GetPriority()
        print "Priority Name: %s" % logging_event_data.GetPriorityName()
        print "Timestamp: %s" % logging_event_data.GetTimestamp()
        print "NDC: %s" % logging_event_data.GetNDC()
        print "Thread: %s" % logging_event_data.GetThreadName()
        print "Message: %s" % logging_event_data.GetLogMessage()
        print "------------------------------------\n"


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

    # Create and register the logging event handler
    #
    # *** NOTES ***
    # Logging events are registered to the system. Take note that a logging
    # event handler is very verbose when the logging level is set to debug.
    #
    # *** LATER ***
    # Logging events must be unregistered manually. This must be done prior to
    # releasing the system and while the device events are still in scope.
    logging_event_handler = LoggingEventHandler()
    system.RegisterLoggingEvent(logging_event_handler)

    # Set callback priority level
    #
    # *** NOTES ***
    # Please see documentation for up-to-date information on the logging
    # philosophies of the Spinnaker SDK.
    system.SetLoggingEventPriorityLevel(LOGGING_LEVEL)

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cams = cam_list.GetSize()

    print "Number of cameras detected: %i" % num_cams

    # Clear camera list before releasing system
    cam_list.Clear()

    # Unregister logging event handler
    #
    # *** NOTES ***
    # It is important to unregister all logging events from the system.
    system.UnregisterLoggingEvent(logging_event_handler)

    # Release system
    system.ReleaseInstance()

    raw_input("Done! Press Enter to exit...")


if __name__ == "__main__":
    main()
