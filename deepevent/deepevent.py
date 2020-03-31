#! /usr/bin/python
#-*-coding: utf-8 -*-

from scipy.signal import argrelextrema
import argparse
from pyBTK import btk
import os
from keras.models import model_from_json
from scipy import signal
from numpy import matlib as mb
import numpy as np
from .utils import *


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
	
def main():
	loaded_model_json = loadmodel()
	
	model = loadweight(loaded_model_json)
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-i','--input',help='* input c3d file',type=str)
	parser.add_argument('-o','--output',help=' output c3d file with events',type=str)
	args = parser.parse_args()


	filenameIn = args.input
	if args.output is not None:
		filenameOut = args.output
	else:
		filenameOut = args.input


	acq0 = readc3d(filenameIn)
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

	acqF = saveLFS(acqF,eventLFS,ff,freq,SubjectValue)
	acqF = saveRFS(acqF,eventRFS,ff,freq,SubjectValue)
	acqF = saveLFO(acqF,eventLFO,ff,freq,SubjectValue)
	acqF = saveRFO(acqF,eventRFO,ff,freq,SubjectValue)

	savec3d(acqF,filenameOut)
	
	

	
	
	