#!/usr/bin/env python3
"""
Complete People Counter with all features
Uses MobileNet SSD for detection and improved CentroidTracker for tracking
Includes all features from original version: email alerts, logging, scheduler, timer, threading
"""

import cv2
import numpy as np
import argparse
import time
import datetime
import imutils
import threading
import schedule
import logging
import json
import csv
from itertools import zip_longest
from imutils.video import VideoStream
from imutils.video import FPS
from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from utils import thread
from dbConnect import PeopleCounterDB, PeopleCounterLogger
from dbConnect.simple_async_logger import SimpleAsyncLogger

# execution start time
start_time = time.time()

# setup logger
logging.basicConfig(level = logging.INFO, format = "[INFO] %(message)s")
logger = logging.getLogger(__name__)

# Load configuration
try:
    with open("utils/config.json", "r") as file:
        config = json.load(file)
except FileNotFoundError:
    # Default config if file doesn't exist
    config = {
        "url": 0,
        "Thread": False,
        "Email_Receive": "admin@example.com",
        "Threshold": 10,
        "ALERT": False,
        "Log": True,
        "Timer": False,
        "Scheduler": False
    }

def parse_arguments():
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--prototxt", required=True,
		help="path to Caffe 'deploy' prototxt file")
	ap.add_argument("-m", "--model", required=True,
		help="path to Caffe pre-trained model")
	ap.add_argument("-i", "--input", type=str,
		help="path to optional input video file")
	ap.add_argument("-o", "--output", type=str,
		help="path to optional output video file")
	ap.add_argument("-c", "--confidence", type=float, default=0.3,
		help="minimum probability to filter weak detections")
	ap.add_argument("-s", "--skip-frames", type=int, default=3,
		help="# of skip frames between detections")
	args = vars(ap.parse_args())
	return args

def send_mail():
	# function to send the email alerts
	try:
		from utils.mailer import Mailer
		Mailer().send(config["Email_Receive"])
		logger.info("Email alert sent successfully")
	except ImportError:
		logger.warning("Mailer module not available, skipping email alert")
	except Exception as e:
		logger.error(f"Failed to send email: {e}")

def log_data(move_in, in_time, move_out, out_time, db_logger=None):
	# function to log the counting data
	data = [move_in, in_time, move_out, out_time]
	# transpose the data to align the columns properly
	export_data = zip_longest(*data, fillvalue = '')

	# Ensure logs directory exists
	import os
	os.makedirs('utils/data/logs', exist_ok=True)

	with open('utils/data/logs/counting_data.csv', 'w', newline = '') as myfile:
		wr = csv.writer(myfile, quoting = csv.QUOTE_ALL)
		if myfile.tell() == 0: # check if header rows are already existing
			wr.writerow(("Move In", "In Time", "Move Out", "Out Time"))
			wr.writerows(export_data)
	
	# Log to database if logger is available
	if db_logger:
		db_logger.log_movement_data(move_in, in_time, move_out, out_time)

def log_person_movement(objectID, direction, centroid, bounding_box, totalFrames, simple_logger=None):
	"""
	Helper function to log confirmed in/out events asynchronously
	Only logs confirmed movements, not real-time data
	"""
	if simple_logger:
		simple_logger.log_event_async(
			event_type=direction,
			person_id=objectID,
			centroid=centroid,
			bounding_box=bounding_box,
			confidence=0.95,  # Default confidence
			frame_number=totalFrames
		)

def people_counter_complete():
	"""
	Complete people counter with all features from original version
	"""
	args = parse_arguments()
	
	# Initialize database connection and simple async logger
	db_instance = None
	db_logger = None
	simple_logger = None
	
	try:
		# Import datetime explicitly to avoid conflicts
		from datetime import datetime as dt
		
		db_instance = PeopleCounterDB()
		if db_instance.test_connection():
			logger.info("Database connection established")
			
			# Initialize simple async logger for confirmed events only
			simple_logger = SimpleAsyncLogger(
				db_instance=db_instance,
				max_queue_size=100  # Small queue for events only
			)
			
			# Start session
			session_name = f"People Counter Session - {dt.now().strftime('%Y-%m-%d %H:%M')}"
			input_source = args.get("input", "webcam")
			session_id = db_instance.start_session({
				'session_name': session_name,
				'input_source': input_source
			})
			
			if session_id:
				logger.info(f"Database session started: {session_id}")
				# Start simple async logger
				if simple_logger.start(session_id):
					logger.info("Simple async logger started - only logging confirmed in/out events")
				else:
					logger.warning("Failed to start simple async logger")
					simple_logger = None
			
			# Keep CSV logger as fallback
			db_logger = PeopleCounterLogger(enable_csv=True, enable_db=False)
		else:
			logger.warning("Database connection failed, using CSV logging only")
			db_logger = PeopleCounterLogger(enable_csv=True, enable_db=False)
	except Exception as e:
		logger.warning(f"Database initialization failed: {e}, using CSV logging only")
		db_logger = PeopleCounterLogger(enable_csv=True, enable_db=False)
	
	# initialize the list of class labels MobileNet SSD was trained to
	# detect, then generate a set of bounding box colors for each class
	CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
		"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
		"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
		"sofa", "train", "tvmonitor"]

	# load our serialized model from disk
	logger.info("Loading MobileNet SSD model...")
	net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

	# if a video path was not supplied, grab a reference to the ip camera
	if not args.get("input", False):
		logger.info("Starting the live stream..")
		vs = VideoStream(config["url"]).start()
		time.sleep(2.0)

	# otherwise, grab a reference to the video file
	else:
		logger.info("Starting the video..")
		vs = cv2.VideoCapture(args["input"])

	# initialize the video writer (we'll instantiate later if need be)
	writer = None

	# initialize the frame dimensions (we'll set them as soon as we read
	# the first frame from the video)
	W = None
	H = None

	# instantiate our centroid tracker with better parameters
	ct = CentroidTracker(maxDisappeared=15, maxDistance=80)
	trackableObjects = {}

	# initialize the total number of frames processed thus far, along
	# with the total number of objects that have moved either up or down
	totalFrames = 0
	totalDown = 0
	totalUp = 0
	
	# initialize empty lists to store the counting data
	total = []
	move_out = []
	move_in =[]
	out_time = []
	in_time = []

	# start the frames per second throughput estimator
	fps = FPS().start()

	# Initialize threading if enabled
	if config["Thread"]:
		vs = thread.ThreadingClass(config["url"])

	# Store previous detections for better tracking
	prev_rects = []

	# loop over frames from the video stream
	while True:
		# grab the next frame and handle if we are reading from either
		# VideoCapture or VideoStream
		frame = vs.read()
		frame = frame[1] if args.get("input", False) else frame

		# if we are viewing a video and we did not grab a frame then we
		# have reached the end of the video
		if args["input"] is not None and frame is None:
			break

		# resize the frame to have a maximum width of 500 pixels (the
		# less data we have, the faster we can process it)
		frame = imutils.resize(frame, width = 500)

		# if the frame dimensions are empty, set them
		if W is None or H is None:
			(H, W) = frame.shape[:2]

		# if we are supposed to be writing a video to disk, initialize
		# the writer
		if args["output"] is not None and writer is None:
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			writer = cv2.VideoWriter(args["output"], fourcc, 30,
				(W, H), True)

		# initialize the current status along with our list of bounding
		# box rectangles returned by either (1) our object detector or
		# (2) the correlation trackers
		status = "Waiting"
		rects = []

		# check to see if we should run a more computationally expensive
		# object detection method to aid our tracker
		if totalFrames % args["skip_frames"] == 0:
			# set the status and initialize our new set of object trackers
			status = "Detecting"

			# convert the frame to a blob and pass the blob through the
			# network and obtain the detections
			blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
			net.setInput(blob)
			detections = net.forward()

			# loop over the detections
			for i in np.arange(0, detections.shape[2]):
				# extract the confidence (i.e., probability) associated
				# with the prediction
				confidence = detections[0, 0, i, 2]

				# filter out weak detections by requiring a minimum
				# confidence
				if confidence > args["confidence"]:
					# extract the index of the class label from the
					# detections list
					idx = int(detections[0, 0, i, 1])

					# if the class label is not a person, ignore it
					if CLASSES[idx] != "person":
						continue

					# compute the (x, y)-coordinates of the bounding box
					# for the object
					box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
					(startX, startY, endX, endY) = box.astype("int")

					# add the bounding box coordinates to the rectangles list
					rects.append((startX, startY, endX, endY))

			# Store current detections for next frame
			prev_rects = rects.copy()

		else:
			# Use previous detections for tracking between detection frames
			status = "Tracking"
			rects = prev_rects

		# draw a horizontal line in the center of the frame -- once an
		# object crosses this line we will determine whether they were
		# moving 'up' or 'down'
		cv2.line(frame, (0, H // 2), (W, H // 2), (0, 255, 0), 2)
		cv2.putText(frame, "-Prediction border - Entrance-", (10, H - ((i * 20) + 200)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

		# use the centroid tracker to associate the (1) old object
		# centroids with (2) the newly computed object centroids
		objects = ct.update(rects)

		# loop over the tracked objects
		for (objectID, centroid) in objects.items():
			# check to see if a trackable object exists for the current
			# object ID
			to = trackableObjects.get(objectID, None)

			# if there is no existing trackable object, create one
			if to is None:
				to = TrackableObject(objectID, centroid)

			# otherwise, there is a trackable object so we can utilize it
			# to determine direction
			else:
				# the difference between the y-coordinate of the *current*
				# centroid and the mean of *previous* centroids will tell
				# us in which direction the object is moving (negative for
				# 'up' and positive for 'down')
				y = [c[1] for c in to.centroids]
				direction = centroid[1] - np.mean(y)
				to.centroids.append(centroid)

				# check to see if the object has been counted or not
				if not to.counted:
					# if the direction is negative (indicating the object
					# is moving up) AND the centroid is above the center
					# line, count the object
					if direction < 0 and centroid[1] < H // 2:
						totalUp += 1
						date_time = dt.now().strftime("%Y-%m-%d %H:%M")
						move_out.append(totalUp)
						out_time.append(date_time)
						to.counted = True
						logger.info(f"Person {objectID} exited (moving up)")
						
						# Log confirmed out event to database asynchronously (non-blocking)
						log_person_movement(objectID, 'out', centroid, (startX, startY, endX, endY), totalFrames, simple_logger)

					# if the direction is positive (indicating the object
					# is moving down) AND the centroid is below the
					# center line, count the object
					elif direction > 0 and centroid[1] > H // 2:
						totalDown += 1
						date_time = dt.now().strftime("%Y-%m-%d %H:%M")
						move_in.append(totalDown)
						in_time.append(date_time)
						
						# Log confirmed in event to database asynchronously (non-blocking)
						log_person_movement(objectID, 'in', centroid, (startX, startY, endX, endY), totalFrames, simple_logger)
						
						# if the people limit exceeds over threshold, send an email alert
						if sum(total) >= config["Threshold"]:
							cv2.putText(frame, "-ALERT: People limit exceeded-", (10, frame.shape[0] - 80),
								cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
							if config["ALERT"]:
								logger.info("Sending email alert..")
								email_thread = threading.Thread(target = send_mail)
								email_thread.daemon = True
								email_thread.start()
								logger.info("Alert sent!")
							
							# Log alert to database
							if db_logger:
								db_logger.check_and_log_alert(sum(total), config["Threshold"])
						
						to.counted = True
						logger.info(f"Person {objectID} entered (moving down)")

				# compute the sum of total people inside (update after each counting)
				total = []
				total.append(len(move_in) - len(move_out))

			# store the trackable object in our dictionary
			trackableObjects[objectID] = to

			# draw both the ID of the object and the centroid of the
			# object on the output frame
			text = "ID {}".format(objectID)
			cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

		# Draw bounding boxes for detected objects
		for (startX, startY, endX, endY) in rects:
			cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

		# construct a tuple of information we will be displaying on the
		# frame
		info_status = [
			("Exit", totalUp),
			("Enter", totalDown),
			("Status", status),
			("Objects", len(objects)),
		]

		info_total = [
			("Total people inside", ', '.join(map(str, total))),
		]

		# display the output
		for (i, (k, v)) in enumerate(info_status):
			text = "{}: {}".format(k, v)
			cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

		for (i, (k, v)) in enumerate(info_total):
			text = "{}: {}".format(k, v)
			cv2.putText(frame, text, (265, H - ((i * 20) + 60)),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

			# initiate a simple log to save the counting data
	# CSV logging temporarily disabled - using database only
	# if config["Log"]:
	#	log_data(move_in, in_time, move_out, out_time, db_logger)
		
		# Note: Real-time metrics logging removed - only log confirmed in/out events

		# check to see if we should write the frame to disk
		if writer is not None:
			writer.write(frame)

		# show the output frame
		cv2.imshow("Real-Time Monitoring/Analysis Window", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

		# increment the total number of frames processed thus far and
		# then update the FPS counter
		totalFrames += 1
		fps.update()

		# initiate the timer
		if config["Timer"]:
			# automatic timer to stop the live stream (set to 8 hours/28800s)
			end_time = time.time()
			num_seconds = (end_time - start_time)
			if num_seconds > 28800:
				break

	# stop the timer and display FPS information
	fps.stop()
	logger.info("Elapsed time: {:.2f}".format(fps.elapsed()))
	logger.info("Approx. FPS: {:.2f}".format(fps.fps()))
	logger.info("Final Count - Enter: {}, Exit: {}, Inside: {}".format(totalDown, totalUp, totalDown - totalUp))
	
	# Cleanup simple async logger
	if simple_logger:
		logger.info("Stopping simple async logger...")
		simple_logger.stop()
		logger.info(f"Simple async logger stats: {simple_logger.get_stats()}")
	
	# End database session
	if db_instance and session_id:
		db_instance.end_session('completed')
		logger.info("Database session ended")

	# check to see if we need to release the video writer pointer
	if writer is not None:
		writer.release()

	# release the camera device/resource
	if config["Thread"]:
		vs.release()

	# if we are not using a video file, stop the camera video stream
	if args["input"] is None:
		vs.stop()

	# otherwise, release the video file pointer
	else:
		vs.release()

	# close any open windows
	cv2.destroyAllWindows()

# initiate the scheduler
if config["Scheduler"]:
	# runs at every day (09:00 am)
	schedule.every().day.at("09:00").do(people_counter_complete)
	while True:
		schedule.run_pending()
# Note: people_counter_complete() is called only in __main__ block

if __name__ == "__main__":
	people_counter_complete()
