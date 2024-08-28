import sys
sys.path.insert(1, '..\\..\\')

import os
import data_loader
from numpy import trapz
import matplotlib.pyplot as plt
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from mlxtend.plotting import plot_confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

malware_data_dir = '../../data/'
saved_model_path = 'saved_model/'
#opcode_to_int_path = "opcodeToInt.txt"
num_unique_opcodes = 30
max_opcode_sequence_length = 2000
embed_vector_length = 128
num_lstm_unit = 16
dropout_amt = 0.3
batch_size = 32
num_epochs = 100
test_size= 0.15       # reserve for testing
results_path = "results.txt"
#num_families_to_use = 20

def split_data(train_data_raw, train_labels_raw):
    # Split into training and testing data
    train_data, test_data, train_labels, test_labels = train_test_split(train_data_raw, train_labels_raw, test_size=test_size)

    # Make divisible by batch size
    num_data_train = int(len(train_data)/batch_size) * batch_size
    num_data_test = int(len(test_data)/batch_size) * batch_size

    train_data = train_data[:num_data_train]
    train_labels = train_labels[:num_data_train]
    test_data = test_data[:num_data_test]
    test_labels = test_labels[:num_data_test]

    return train_data, test_data, train_labels, test_labels

def create_model(num_families_to_use):
    model = Sequential()
    model.add(LSTM(units=num_lstm_unit, 
                    input_shape=(max_opcode_sequence_length, 1),
                    name="lstm1"))
    model.add(Dropout(dropout_amt))
    model.add(Dense(units=num_families_to_use, activation='softmax', name="dense"))
    optimizer = Adam()
    model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    model.summary()
    
    return model

num_families_to_use = 20
results = {}

# with open(results_path, 'a') as file:
#     file.write(str(num_families_to_use) + "\n")

opcode_to_int_path = "opcodeToInt_" + str(num_families_to_use) + ".txt"
# Get train data
raw_train_data = data_loader.getTrainData(malware_data_dir, 
                                          num_families_to_use, 
                                          num_unique_opcodes, 
                                          max_opcode_sequence_length, 
                                          opcode_to_int_path)
# Data preprocessing
family_names = list(raw_train_data.keys())
print(family_names)

# Split opcode family data in individual lists
train_data = list()
for family, data in raw_train_data.items():
    train_data.append(data)

# Pad training data to ensure uniformity
padded_train_data = list()
for family_opcodes in train_data:
    padded_sequence = pad_sequences(family_opcodes, 
                                    maxlen=max_opcode_sequence_length)
    padded_train_data.append(padded_sequence)

# Concatenate all training data into 1 long list instead of multiple lists
train_data_raw = np.concatenate(padded_train_data)

print(len(train_data))

# Make labels
train_labels = []
for count, data in enumerate(padded_train_data):
    labels_list = np.full(shape=(len(data)), fill_value=count)
    train_labels.append(labels_list)

train_labels_raw = np.concatenate(train_labels)

train_data_raw = train_data_raw.reshape(len(train_data_raw), max_opcode_sequence_length, 1)
train_labels_raw = train_labels_raw.reshape(len(train_data_raw), 1, 1)


# get train and test data
train_data, test_data, train_labels, test_labels = split_data(train_data_raw, train_labels_raw)

# train model
model_train = create_model(num_families_to_use)
early_stopping = EarlyStopping(monitor='loss', 
                               verbose=1, 
                               patience=2,
                               restore_best_weights=True,
                                min_delta=0.03)
# history = model_train.fit(x=train_data,
#                           y=train_labels,
#                           batch_size=batch_size,
#                           callbacks = [early_stopping],
#                           epochs=num_epochs,
#                           shuffle=True)

# model_train.save_weights(saved_model_path) 

## evaluate
model_evaluate = create_model(num_families_to_use)
model_evaluate.load_weights(saved_model_path)

scores = model_evaluate.evaluate(test_data, test_labels, verbose=0, callbacks = [early_stopping])
accuracy = scores[1]*100
print("{0}: {1}".format(num_families_to_use, accuracy))
results[num_families_to_use] = accuracy

#             with open(results_path, 'a') as file:
#                 file.write(str(accuracy) + "\n")

predictions_train_set = model_evaluate.predict_classes(train_data, verbose=1)
predictions_test_set = model_evaluate.predict_classes(test_data, verbose=1)
labels_train_set = train_labels.reshape((-1))
labels_test_set = test_labels.reshape((-1))

predictions = np.concatenate((predictions_train_set, predictions_test_set))
labels = np.concatenate((labels_train_set, labels_test_set))

matrix = confusion_matrix(y_true=labels,
                            y_pred=predictions)

np.set_printoptions(threshold=sys.maxsize)
print("true: {0}".format(labels))
print("predictions: {0}".format(predictions))

fig, ax = plot_confusion_matrix(conf_mat=matrix,
                                show_absolute=False,
                                show_normed=True,
                                class_names=family_names,
                                figsize=(12,12))

for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(10)


ax.set_title("Confusion Matrix for LSTM Model With No Embedding", fontsize=15, fontweight='bold')
ax.set_ylabel("True Family", fontsize=12, fontweight='bold')
ax.set_xlabel("Predicted Family", fontsize=12, fontweight='bold')

plt.show()


