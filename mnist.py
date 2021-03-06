#!/usr/bin/env python3

import pdb
import aux
import mxnet as mx
import numpy as np
from mxnet import gluon, nd, autograd

# Define number of training-cases, features, and classes
m_cases = 25112
d_inputs = 784
k_outputs = 5

# Maximum number of epochs
epochs = 12

# Define the learning rate
learn_rate = 0.5

# Run everything on CPU
cntx = mx.cpu()

# Provide the relative or absolute data path
path = 'data/'

# import training and test data
X_train, Y_train = aux.load_mnist(path,'train')
X_test, Y_test = aux.load_mnist(path,'test')

# Set batch_size to 1 as we are using SGD
batch_size = 1

# Load the data iterator for SGD
train_data = gluon.data.DataLoader(gluon.data.ArrayDataset(X_train, Y_train),
                                   batch_size, shuffle=True)
test_data = gluon.data.DataLoader(gluon.data.ArrayDataset(X_test, Y_test),
                                  batch_size, shuffle=False)

# Initialize weights and biases for each class
W = nd.random_normal(shape=(d_inputs,k_outputs),ctx=cntx)
W0= nd.random_normal(shape=k_outputs,ctx=cntx)
prams = [W, W0]


# Track the gradients of the parameters
for parameter in prams:
    parameter.attach_grad()

# Execute training loop using SGD
for E in range(epochs):
    total_loss = 0
    for i, (xtrain, ytrain) in enumerate(train_data):
        xtrain = xtrain.as_in_context(cntx).reshape((-1,784))
        ytrain = ytrain.as_in_context(cntx)
        ylabel_flag = nd.one_hot(ytrain,5)
        with autograd.record():
            y_out = aux.nnet(xtrain,W,W0)
            loss = aux.cross_ent(y_out, ylabel_flag)
        loss.backward()
        prams = aux.SGD(prams, learn_rate)
        total_loss += nd.sum(loss).asscalar()

    # Evaluate model on training data
    train_accuracy = aux.compute_accuracy(train_data, aux.nnet, prams, cntx)

    # Evaluate model on testing data
    test_accuracy = aux.compute_accuracy(test_data, aux.nnet, prams, cntx)
    print("Epoch %s. Loss: %s, Train Accuracy: %s, Test Accuracy: %s" %
          (E, total_loss/m_cases, train_accuracy, test_accuracy))

    # Save trained parameters
    aux.save_mnist(prams)
