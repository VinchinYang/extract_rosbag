'''

This script extracts images from ros bag files and stores them in specified folder 
with image names as corresponding timestamps. 

This script is the modified version of bag_to_csv script written by Nick Speal in May 2013 at McGill University's Aerospace Mechatronics Laboratory
www.speal.ca

'''

import rosbag, sys, csv
import time
import string
import os #for file management make directory
import shutil #for file management, copy file
from cv_bridge import CvBridge
import cv2

#verify correct input arguments: 1 or 2
if (len(sys.argv) > 2):
	print "invalid number of arguments:   " + str(len(sys.argv))
	print "should be 2: 'bag2csv.py' and 'bagName'"
	print "or just 1  : 'bag2csv.py'"
	sys.exit(1)
elif (len(sys.argv) == 2):
	listOfBagFiles = [sys.argv[1]]
	numberOfFiles = "1"
	print "reading only 1 bagfile: " + str(listOfBagFiles[0])
elif (len(sys.argv) == 1):
	listOfBagFiles = [f for f in os.listdir(".") if f[-4:] == ".bag"]	#get list of only bag files in current dir.
	numberOfFiles = str(len(listOfBagFiles))
	print "reading all " + numberOfFiles + " bagfiles in current directory: \n"
	for f in listOfBagFiles:
		print f
	print "\n press ctrl+c in the next 2 seconds to cancel \n"
	time.sleep(2)
else:
	print "bad argument(s): " + str(sys.argv)	#shouldnt really come up
	sys.exit(1)

count = 0
bridge = CvBridge()
for bagFile in listOfBagFiles:
	count += 1
	print "reading file " + str(count) + " of  " + numberOfFiles + ": " + bagFile
	#access bag
	bag = rosbag.Bag(bagFile)
	bagContents = bag.read_messages()
	bagName = bag.filename


	#create a new directory
	folder = string.rstrip(bagName, ".bag")
	try:	#else already exists
		os.makedirs(folder)
		os.makedirs(folder + '/rosbag_images')
	except:
		pass
	# shutil.copyfile(bagName, folder + '/' + bagName)


	#get list of topics from the bag
	listOfTopics = []
	for topic, msg, t in bagContents:
		if topic not in listOfTopics:
			listOfTopics.append(topic)


	for topicName in listOfTopics:
		#Create a new CSV file for each topic
		filename = folder + '/' + string.replace(topicName, '/', '_timestamps_') + '.csv'
		print(topicName)

		if topicName == '/mti/sensor/imu':
			with open(filename, 'w+') as csvfile:
				filewriter = csv.writer(csvfile, delimiter = ',')
				for subtopic, msg, t in bag.read_messages(topicName):
					# print(msg.orientation.w)
					print(msg)
					msg_list = []
					msg_list.append(str(t))
					msg_list.append(msg.orientation.x)
					msg_list.append(msg.orientation.y)
					msg_list.append(msg.orientation.z)
					msg_list.append(msg.orientation.w)
					msg_list.append(msg.angular_velocity.x)
					msg_list.append(msg.angular_velocity.y)
					msg_list.append(msg.angular_velocity.z)	
					msg_list.append(msg.linear_acceleration.x)
					msg_list.append(msg.linear_acceleration.y)
					msg_list.append(msg.linear_acceleration.z)
					filewriter.writerow(msg_list)		
		if topicName=='/usb_cam/image_raw':
			with open(filename, 'w+') as csvfile:
				filewriter = csv.writer(csvfile, delimiter = ',')
				firstIteration = False	#allows header row
				for subtopic, msg, t in bag.read_messages(topicName):	# for each instant in time that has data for topicName
					if subtopic=='/usb_cam/image_raw':
						filewriter.writerow([str(t)])
						cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
				                # print('subtopic',subtopic)
				                print('t',str(t))
						cv2.imwrite(folder + '/rosbag_images/'+str(t)+'.jpg',cv_img)

	bag.close()
print "Done reading all " + numberOfFiles + " bag files."
