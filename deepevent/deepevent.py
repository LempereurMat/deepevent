#!/usr/bin/python
import os
import argparse
from keras.models import model_from_json
import btk
import numpy as np
from scipy import signal
from scipy.signal import argrelextrema
from numpy import matlib as mb


def filter(acq,marker,fc):
	# Butterworth filter
	b, a = signal.butter(4, fc/(acq.GetPointFrequency()/2))
	Mean = np.mean(marker,axis=0)
	Minput = marker - mb.repmat(Mean,acq.GetPointFrameNumber(),1)	
	Minput = signal.filtfilt(b,a,Minput,axis=0)
	Moutput = Minput + np.matlib.repmat(Mean,acq.GetPointFrameNumber(),1)
	return Moutput

def derive_centre(acq,marker):
	# Compute velocity
	marker_der = (marker[2:acq.GetPointFrameNumber(),:] - marker[0:(acq.GetPointFrameNumber()-2),:]) / (2 / acq.GetPointFrequency()) 
	marker_der = np.concatenate(([[0,0,0]],marker_der,[[0,0,0]]),axis=0)
	return marker_der


def compute(FilenameIn,FilenameOut):
	json_file = open('deepevent/data/DeepEventModel.json','r')
	loaded_model_json = json_file.read()
	json_file.close()
	load_model = model_from_json(loaded_model_json)
	load_model.load_weights("deepevent/data/DeepEventWeight.h5")

	#Read the FilenameIn.c3d
	reader = btk.btkAcquisitionFileReader() 
	reader.SetFilename(FilenameIn)
	reader.Update()
	acq = reader.GetOutput()
	
	markers = ["LANK","RANK","LTOE","RTOE","LHEE","RHEE"]
	nframes = 1536
	nb_data_in = 36 #6 markers x 3

	# Filter and derivate the input
	inputs = np.zeros((1,nframes,nb_data_in))
	for k in range(6):
		inputs[0,0:acq.GetPointFrameNumber(),k*3: (k + 1)*3] = filter(acq,acq.GetPoint(markers[k]).GetValues(),6)
		inputs[0,0:acq.GetPointFrameNumber(),3 * len(markers) + k*3:3 * len(markers) +  (k + 1)*3] = derive_centre(acq,inputs[0,:,k * 3:(k+1)*3])
	
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
		if np.sum(predicted_seuil_max[0,j,:]) == 0:
			predicted_seuil_max[0,j,0] = 1
	
	eventLFS = np.argwhere(predicted_seuil_max[0,:,1])
    	for ind_indice in range(eventLFS.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("FootStrike")
		newEvent.SetContext("Left")
		newEvent.SetTime((acq.GetFirstFrame()-1)/acq.GetPointFrequency() + float(eventLFS[ind_indice]/acq.GetPointFrequency()))
		newEvent.SetId(1)
		acq.AppendEvent(newEvent)
		
	eventRFS = np.argwhere(predicted_seuil_max[0,:,2])
	for ind_indice in range(eventRFS.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("FootStrike")
		newEvent.SetContext("Right") 
		newEvent.SetTime((acq.GetFirstFrame()-1)/acq.GetPointFrequency() + float(eventRFS[ind_indice]/acq.GetPointFrequency()))
		newEvent.SetId(1)
		acq.AppendEvent(newEvent)			

	eventLFO = np.argwhere(predicted_seuil_max[0,:,3])
	for ind_indice in range(eventLFO.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("FootOff")
		newEvent.SetContext("Left") #
		newEvent.SetTime((acq.GetFirstFrame()-1)/acq.GetPointFrequency() + float(eventLFO[ind_indice]/acq.GetPointFrequency()))
		newEvent.SetId(2)
		acq.AppendEvent(newEvent)			

	eventRFO = np.argwhere(predicted_seuil_max[0,:,4])
	for ind_indice in range(eventRFO.shape[0]):
		newEvent=btk.btkEvent()
		newEvent.SetLabel("FootOff")
		newEvent.SetContext("Right") #
		newEvent.SetTime((acq.GetFirstFrame()-1)/acq.GetPointFrequency() + float(eventRFO[ind_indice]/acq.GetPointFrequency()))
		newEvent.SetId(2)
		acq.AppendEvent(newEvent)

	#Write the FilenameOut.c3d
	writer = btk.btkAcquisitionFileWriter()
	writer.SetInput(acq)
	writer.SetFilename(FilenameOut)
	writer.Update()


parser = argparse.ArgumentParser()
parser.add_argument('FilenameIn',help='*.c3d file',type=str)
parser.add_argument('FilenameOut',help='*.c3d file with events',type=str,default='FilenameOut.c3d')
args = parser.parse_args()

compute(args.FilenameIn,args.FilenameOut)

