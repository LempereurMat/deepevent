# DeepEvent Version 0.4



We propose a new application (_DeepEvent_) of long short term memory recurrent neural network to the automatic detection of gait events.
The 3D position and velocity of the markers on the heel, toe and lateral malleolus were used by the network to determine Foot Strike (FS) and Foot Off (FO).
The method was developed from  10526 FS and 9375 FO from 226 children. _DeepEvent_ predicted **FS** within **5.5 ms** and **FO** within **10.7 ms** of the gold standard (automatic determination using force platform data) and was more accurate than common heuristic marker trajectory-based methods proposed in the literature and another deep learning method.


## Requirement


Windows 64 bits only, python3.7, Keras, Tensorflow, pyBtk, Numpy, Scipy, GoogleDriveDownloader

All depedancies are available in pipy  



## Installation
```sh
pip install deepevent==0.4
```



## Running _DeepEvent_
```sh
deepevent  -i FilenameIn.c3d -o FilenameOut.c3d
deepevent  --input FilenameIn.c3d --output FilenameOut.c3d
deepevent  --input FilenameIn.c3d
```
where FilenameIn.c3d is the c3d file to identify gait events, FilenameOut.c3d is the new file with the gait events.  
In the last case, filenameIn.c3d is overwritten with gait events

## Bibliography
Lempereur M., Rousseau F., Rémy-Néris O., Pons C., Houx L., Quellec G., Brochard S. (2019). [A new deep learning-based method for the detection of gait events in children with gait disorders: Proof-of-concept and concurrent validity](https://doi.org/10.1016/j.jbiomech.2019.109490). Journal of Biomechanics. Volume 98, 2 January 2020, 109490.




## Contacts
**Original developer**
[mathieu.lempereur@univ-brest.fr](mailto:mathieu.lemepreur@univ-brest.fr)  
Mathieu LEMPEREUR  
CHRU de Brest - Hopital Morvan  
Service MPR  
2 avenue Foch  
29609 BREST cedex  
FRANCE

**Forked developer**
[fabien.leboeuf@gmail.com](mailto:fabien.leboeuf@gmail.com)<br/>
Fabien Leboeuf<br/>
Ingénieur "analyste du mouvement" du Pole 10, CHU Nantes, France<br/>
Chercheur associé de l'Université de Salford, Manchester, Royaume uni<br/>
Laboraratoire d'analyse du mouvement<br/>
85 rue saint Jacques<br/>
44093 Nantes<br/>
FRANCE

## Licence
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-nc-sa/4.0/)
