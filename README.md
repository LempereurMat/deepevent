# DeepEvent
---
We propose a new application (_DeepEvent_) of long short term memory recurrent neural network to the automatic detection of gait events.
The 3D position and velocity of the markers on the heel, toe and lateral malleolus were used by the network to determine Foot Strike (FS) and Foot Off (FO). 
The method was developed from  10526 FS and 9375 FO from 226 children. _DeepEvent_ predicted **FS** within **5.5 ms** and **FO** within **10.7 ms** of the gold standard (automatic determination using force platform data) and was more accurate than common heuristic marker trajectory-based methods proposed in the literature and another deep learning method.

---
## Requirement
Linux, Python 2.7, Keras, Tensorflow, Btk, Numpy, Scipy.

---
## Installation
`pip install deepevent`

---
## Running _DeepEvent_
`deepevent FilenameIn.c3d FilenameOut.c3d`
where FilenameIn.c3d is the c3d file to identify gait events, FilenameOut.c3d is the new file with the gait events.

---
## Next step
Python 3.7, Windows

---
## Contact
[mathieu.lempereur@univ-brest.fr](mailto:mathieu.lemepreur@univ-brest.fr)
Mathieu LEMPEREUR
CHRU de Brest - Hopital Morvan
Service MPR
2 avenue Foch
29609 BREST cedex
FRANCE