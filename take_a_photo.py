import pyspin
from pyspin import PySpin

# Get system
system = PySpin.System.GetInstance()

# Get camera list
cam_list = system.GetCameras()

# Figure out which is primary and secondary (usually webcam is primary and Flea3 is secondary)
cam = cam_list.GetByIndex(0)

# Initialize camera
cam.Init()

# Set acquisition mode
cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)

# Start acquisition
cam.BeginAcquisition()

# Acquire images
image_primary = cam.GetNextImage()
width = image_primary.GetWidth()
height = image_primary.GetHeight()
print "width: " + str(width) + ", height: " + str(height)

# Save images
image_primary.Save('prime.jpg')

# Stop acquisition
cam.EndAcquisition()

# De-initialize
cam.DeInit()

# Clear references to images and cameras
del image_primary
del cam
del cam_list
