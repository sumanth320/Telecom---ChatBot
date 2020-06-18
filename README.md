# Telecom---ChatBot

# Chatbot: Using Keras with Tensorflow as "Backend-Engine" and python.

## System Requirements
Make sure you have the Python 3.7.6  installed
IDE : Anaconda(Jupyter and Spyder),Pycharm.

## Installation
- Create a virtual enviornment: This is a good practice but not necessary
	- Goto Anaconda Prompt and type in the below command. This command will create a virtual enviornment.
	conda create -y --name tensorflow python=3.7
	- Now activate the virtual enviornment, by executing the below command. This command will change the prompt from "base" to "tensorflow"
	activate tensorflow
	
- In the Terminal type the following commands to install the libraries,this will check the exsisiting version and will install the latest one.
	- conda install -y scipy
	- pip install --exists-action i --upgrade tensorflow==2.0.0
	- pip install --exists-action i --upgrade keras
	- pip install --exists-action i --upgrade nltk
	- pip install --exists-action i --upgrade numpy
	- pip install --exists-action i --upgrade pandas
	- pip install --exists-action i --upgrade pickle
	- pip install --exists-action i --upgrade 

- Check the version installed using below commands:
	- tf.__version__  	(where tf is the alias of tensorflow)
	- k.__version__		(where k is the alias of keras)
	- sys.version		
	- pd.__version__	(where pd is the alias of pandas)
	
- Select the virtual Environment:
	- In Anaconda Navigator --> Home, Click on the "Applications on" dropdown and Select "tensorflow".
	- This will take a few minutes, after that install the prefered IDE (Jupyter, Spyder),installation is required for first time only
	- Launch the IDE and start coding.

- In IDE Pycharm : Pycharm uses a virtual enviornment to run tensorflow, hence install the tensorflow to the specific virtual enviornment.
	- Project Setting --> Project Interpreter --> Click on the "+" icon at the bottom left of the package window --> type in tensorflow and specify the version
	- Click on Install Package
	
## Possible Errors

```
tensorboard 2.0.0 has requirement setuptools>=41.0.0, but you'll have setuptools 40.8.0 which is incompatible.
```
This is a possible error which can be solved using the command 
```
pip install --upgrade --user tensorflow
```
## License
Open Source Software

## IDE used for the project: 
Pycharm, Anaconda Jupyter

## Python Libraries :

- for creating model.
	from keras.models import Sequential
- for creating layers for the model.	
	from keras.layers import Dense, Activation, Dropout
- for selecting optimiser for minising loss and hence increasing accuracy.
	from keras.optimizers import Adam,SGD
- for chatbot GUI.
	from tkinter import *  
- for displaying date and time.
	import time
	import datetime
- for processing natural language.
	from nltk import word_tokenize
- wordNet is a collection of nouns and verbs and adjectives and their synonyms
	from nltk.stem import WordNetLemmatizer  
- for create light weight binary files.
	import pickle
- for importing the model created. 
	from keras.models import load_model
- for formating the Intents.json file.
	import json
- for selecting a random "response" from the slected "tag"
	import random
- for converting the bag-of-words (bag) from customer input and feeding it to the model.
	import numpy as np
- for making database related operations(insert, select)
	import sqlite3
- for matching words from customer for unlimited data.
	from fuzzywuzzy import fuzz
- for processing the images used in the aplication.
	from PIL import Image
	from PIL import ImageTk


##General Instructions
- To download the corpus i.e nltk_data either :
1. Run the below command in the terminal window of PyCharm or on the command prompt.
	 python -m nltk.downloader all
2. In your .py file add 2 line:
		import nltk
		nltk.download()
    A pop-up window will apper and click on download --> it will take some time, Once all the collections turn green close the window.
	
	
- Make sure proper libraries are imported while executing and please follow best coding practices.

Happy Coding!

