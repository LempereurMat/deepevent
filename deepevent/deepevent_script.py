# coding: utf-8
import os
import argparse
from keras.models import model_from_json
from pyBTK import btk
import numpy as np
from scipy import signal
from scipy.signal import argrelextrema
from numpy import matlib as mb
import pdb
import logging
import numpy as np
import deepevent
import requests

def filter(acq,marker,fc):
	# Butterworth filter
	b, a = signal.butter(4, fc/(acq.GetPointFrequency()/2))
	Mean = np.mean(marker,axis=0)
	Minput = marker - mb.repmat(Mean,acq.GetPointFrameNumber(),1)
	Minput = signal.filtfilt(b,a,Minput,axis=0)
	Moutput = Minput + np.matlib.repmat(Mean,acq.GetPointFrameNumber(),1)

	return Moutput

def derive_centre(marker,pfn,freq):
	# Compute velocity

	marker_der = (marker[2:pfn,:] - marker[0:(pfn-2),:]) / (2 / freq)
	marker_der = np.concatenate(([[0,0,0]],marker_der,[[0,0,0]]),axis=0)
	return marker_der

def progressionframe(acq,marker="LANK"):
	__threshold = 800
	values = acq.GetPoint(marker).GetValues()

	MaxValues =[values[-1,0]-values[0,0], values[-1,1]-values[0,1]]
	absMaxValues =[np.abs(values[-1,0]-values[0,0]), np.abs(values[-1,1]-values[0,1])]

	ind = np.argmax(absMaxValues)

	if absMaxValues[ind] > __threshold:

		diff = MaxValues[ind]

		if ind ==0 :
			progressionAxis = "X"
			lateralAxis = "Y"
		else:
			progressionAxis = "Y"
			lateralAxis = "X"

		forwardProgression = True if diff>0 else False

		globalFrame = (progressionAxis+lateralAxis+"Z")
	else:
		raise Exception("[deepEvent] progression axis not detected - distance of the marker %s inferior to 800mm"%(marker))

	return globalFrame,forwardProgression


def applyRotation(acq,marker,globalFrameOrientation,forwardProgression):

	if globalFrameOrientation == "XYZ":
		rot = np.array([[1,0,0],[0,1,0],[0,0,1]])
	elif globalFrameOrientation == "YXZ":
		rot = np.array([[0,1,0],[-1,0,0],[0,0,1]])
	else:
		raise Exception("[deepEvent] code cannot work with Z as non-normal axis")

	values = acq.GetPoint(marker).GetValues()

	valuesRot = np.zeros((acq.GetPointFrameNumber(),3))
	for i in range (0, acq.GetPointFrameNumber()):
		valuesRot[i,:]= np.dot(rot,values[i,:])
		if not forwardProgression:
			valuesRot[i,:] = np.dot(np.array([[-1,0,0],[0,1,0],[0,0,1]]),valuesRot[i,:])

	acq.GetPoint(marker).SetValues(valuesRot)

	return acq

def save(acq, filename):
    #Write the FilenameOut.c3d
	writer = btk.btkAcquisitionFileWriter()
	writer.SetInput(acq)
	writer.SetFilename(filename)
	writer.Update()

def read(filename):
	reader = btk.btkAcquisitionFileReader()
	reader.SetFilename(filename)
	reader.Update()
	acq = reader.GetOutput()

	return acq

def predict(load_model,acq,markers,pfn,freq):

	nframes = 1536
	nb_data_in = 36 #6 markers x 3

	inputs = np.zeros((1,nframes,nb_data_in))
	for k in range(6):
		values = acq.GetPoint(markers[k]).GetValues()
		inputs[0,0:pfn,k*3: (k + 1)*3] = filter(acq,values,6)
		inputs[0,0:pfn,3 * len(markers) + k*3:3 * len(markers) +  (k + 1)*3] = derive_centre(inputs[0,:,k * 3:(k+1)*3],pfn,freq)

	# Prediction with the model
	predicted = load_model.predict(inputs) #shape[1,nb_frames,5] 0: no event, 1: Left Foot Strike, 2: Right Foot Strike, 3:Left Toe Off, 4: Right Toe Off

	#Threshold to set the gait events
	predicted_seuil = predicted
	for j in range(nframes):
		if predicted[0,j,1] <= 0.01:
			predicted_seuil[0,j,1] = 0
		if predicted[0,j,2] <= 0.01:
			predicted_seuil[0,j,2] = 0
		if predicted[0,j,3] <= 0.01:
			predicted_seuil[0,j,3] = 0
		if predicted[0,j,4] <= 0.01:
			predicted_seuil[0,j,4] = 0

	predicted_seuil_max = np.zeros((1,nframes,5))
	for j in range(1,5):
		predicted_seuil_max[0,argrelextrema(predicted_seuil[0,:,j],np.greater)[0],j] = 1

	for j in range(nframes):
		if np.sum(predicted_seuil_max[0,j,:]) == 0: predicted_seuil_max[0,j,0] = 1

	eventLFS = np.argwhere(predicted_seuil_max[0,:,1])
	eventRFS = np.argwhere(predicted_seuil_max[0,:,2])
	eventLFO = np.argwhere(predicted_seuil_max[0,:,3])
	eventRFO = np.argwhere(predicted_seuil_max[0,:,4])

	return eventLFS,eventRFS,eventLFO,eventRFO


def main(args):

	json_file = open(deepevent.DATA_PATH+'DeepEventModel.json','r')
	loaded_model_json = json_file.read()
	json_file.close()

	url = 'https://drive.google.com/file/d/1w7LmluewzGbx5EK4V2TIXsUhE953-Oh3/view?usp=sharing'
	r = requests.get(url)
	with open(deepevent.DATA_PATH+"DeepEventWeight.h5", 'wb') as f:
		f.write(r.content)

	model = model_from_json(loaded_model_json)
	model.load_weights(deepevent.DATA_PATH+"DeepEventWeight.h5")

	filenameIn = args.input
	if args.output is not None:
		filenameOut = args.output
	else:
		filenameOut = args.input
		logging.warning("[deepevent] input will be overwritten")


	acq0 = read(filenameIn)
	acq0.ClearEvents()

	acqF = btk.btkAcquisition.Clone(acq0)
	pfn = acqF.GetPointFrameNumber()
	freq = acqF.GetPointFrequency()
	ff = acqF.GetFirstFrame()

	md = acq0.GetMetaData()
	SubjectInfo = md.FindChild("SUBJECTS").value().FindChild("NAMES").value().GetInfo()
	SubjectValue = SubjectInfo.ToString()

	markers = ["LANK","RANK","LTOE","RTOE","LHEE","RHEE"]

	globalFrame,forwardProgression = progressionframe(acq0)
	for marker in markers:
		applyRotation(acq0,marker,globalFrame,forwardProgression)


	eventLFS,eventRFS,eventLFO,eventRFO = predict(model,acq0,markers,pfn,freq)

	for ind_indice in range(eventLFS.shape[0]):
	    newEvent=btk.btkEvent()
	    newEvent.SetLabel("Foot Strike")
	    newEvent.SetContext("Left")
	    newEvent.SetTime((ff-1)/freq + float(eventLFS[ind_indice]/freq))
	    newEvent.SetSubject(SubjectValue[0])
	    newEvent.SetId(1)
	    acqF.AppendEvent(newEvent)

	for ind_indice in range(eventRFS.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("Foot Strike")
		newEvent.SetContext("Right")
		newEvent.SetTime((ff-1)/freq + float(eventRFS[ind_indice]/freq))
		newEvent.SetSubject(SubjectValue[0])
		newEvent.SetId(1)
		acqF.AppendEvent(newEvent)

	for ind_indice in range(eventLFO.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("Foot Off")
		newEvent.SetContext("Left") #
		newEvent.SetTime((ff-1)/freq + float(eventLFO[ind_indice]/freq))
		newEvent.SetSubject(SubjectValue[0])
		newEvent.SetId(2)
		acqF.AppendEvent(newEvent)

	for ind_indice in range(eventRFO.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("Foot Off")
		newEvent.SetContext("Right") #
		newEvent.SetTime((ff-1)/freq + float(eventRFO[ind_indice]/freq))
		newEvent.SetSubject(SubjectValue[0])
		newEvent.SetId(2)
		acqF.AppendEvent(newEvent)

	save(acqF,filenameOut)

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-i','--input',help='* input c3d file',type=str)
	parser.add_argument('-o','--output',help=' output c3d file with events',type=str)
	args = parser.parse_args()


	main(args)

	# args.FilenameIn= "Yaxis_backward_walking.c3d"
	# args.FilenameOut = "Yaxis_backward_walking-OUT.c3d"
	# main(args.FilenameIn,args.FilenameOut)

	# args.FilenameIn= "Yaxis_walking.c3d"
	# args.FilenameOut = "Yaxis_walking-OUT.c3d"
	# compute(args.FilenameIn,args.FilenameOut)
