"""
    Heart attack detection in colour images using convolutional neural networks

    This code make a neural network to detect infarcts
    Written by Gabriel Rojas - 2019
    Copyright (c) 2019 G0 S.A.S.
    Licensed under the MIT License (see LICENSE for details)
"""

import os
import sys
from time import time
import tensorflow
import keras
from keras import backend as K
from keras.models import Sequential
from keras.optimizers import SGD
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dropout, Flatten, Dense, Activation
from keras.layers import  Convolution2D, MaxPooling2D, ZeroPadding2D

# === Configuration vars ===
# Path of image folder (use slash at the end)
INPUT_PATH_TRAIN = "./dataset/train/"
INPUT_PATH_VAL = "./dataset/val/"
INPUT_PATH_TEST = "./dataset/test/"
OUTPUT_DIR = "./model/"

# Checkpoints
EPOCH_CHECK_POINT = 2   # How many epoch til save next checkpoint
NUM_CHECK_POINT = 10    # How many epoch will be saved
KEEP_ONLY_LATEST = False# Keeping only the last checkpoint

# Train configurations
WIDTH, HEIGHT = 256, 256# Size images to train
STEPS = 500             # How many steps per epoch
VALIDATION_STEPS = 100  # How many steps per next validation
BATCH_SIZE = 48         # How many images at the same time, change depending on your GPU
LR = 0.003              # Learning rate
CLASSES = 2             # Don't chage, 0=Infarct, 1=Normal
# === ===== ===== ===== ===

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

K.clear_session()

train_datagen = ImageDataGenerator()
val_datagen = ImageDataGenerator()
test_datagen = ImageDataGenerator()

train_gen = train_datagen.flow_from_directory(
    INPUT_PATH_TRAIN,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')
val_gen = val_datagen.flow_from_directory(
    INPUT_PATH_VAL,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')
test_gen = test_datagen.flow_from_directory(
    INPUT_PATH_TEST,
    target_size=(HEIGHT, WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='categorical')

NET = Sequential()
NET.add(Convolution2D(64, kernel_size=(3 ,3), padding ="same", input_shape=(256, 256, 3), activation='relu'))
NET.add(MaxPooling2D((3,3), strides=(3,3)))
NET.add(Convolution2D(128, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((3,3), strides=(3,3)))
NET.add(Convolution2D(256, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(Convolution2D(512, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(Convolution2D(1024, kernel_size=(3, 3), activation='relu'))
NET.add(MaxPooling2D((2,2), strides=(2,2)))
NET.add(Dropout(0.3))
NET.add(Flatten())

for _ in range(5):
    NET.add(Dense(128, activation='relu'))
NET.add(Dropout(0.5))

for _ in range(5):
    NET.add(Dense(128, activation='relu'))
NET.add(Dropout(0.5))

for _ in range(5):
    NET.add(Dense(128, activation='relu'))
NET.add(Dropout(0.5))

NET.add(Dense(CLASSES, activation='softmax'))

sgd = SGD(lr=LR, decay=1e-4, momentum=0.9, nesterov=True)

NET.compile(optimizer=sgd,
              loss='binary_crossentropy',
              metrics=['acc', 'mse'])

NET.summary()

for i in range(NUM_CHECK_POINT):        
    NET.fit_generator(
        train_gen,
        steps_per_epoch=STEPS,
        epochs=EPOCH_CHECK_POINT,
        validation_data=val_gen,
        validation_steps=VALIDATION_STEPS,
        verbose=1
    )   
    
    print('Saving model: {:02}.'.format(i))
    NET.save(OUTPUT_DIR + "{:02}_model.h5".format(i))
