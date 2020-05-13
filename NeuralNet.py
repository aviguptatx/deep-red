import numpy as np
import pickle
import math
import GameParser
from matplotlib import pyplot as plt

# Initializes a neural network with 2 layers of sizes input_dim and output_dim
def init_network(neural_net):
    np.random.seed(70)
    num_layers = len(neural_net)

    params_w = []
    params_b = []

    for layer in range(0, num_layers):
        # Uses He-et-al Initialization
        temp_w = np.random.randn(neural_net[layer]["k"], neural_net[layer]["j"]) * np.sqrt(2 / neural_net[layer]["j"]) 
        params_w.append(temp_w)
        temp_b = np.random.randn(neural_net[layer]["k"]) * np.sqrt(2 / neural_net[layer]["j"]) 
        params_b.append(temp_b)

    return params_w, params_b

def sigmoid(Z):
    return 1/(1 + np.exp(-Z))

def sigmoid_derivative(Z):
    return sigmoid(Z) * (1 - sigmoid(Z))
 
def forward_prop_layer(prev_A, curr_weights, curr_bias):
    new_vals = np.dot(curr_weights, prev_A) + curr_bias
    return sigmoid(new_vals), new_vals

def test_errors_over_time(params_w, params_b):
    test_set_errors = np.zeros((7, 1))
    # Test set error calculation
    for m in range (np.shape(test_X)[0]):
        error, _ = test_function(params_w, params_b, m)
        test_set_errors += error
    return np.copy(test_set_errors) / np.shape(test_X)[0]

def error_function(params_w, params_b, test_inputs, test_outputs):
    activations0 = [None] * np.shape(test_inputs)[0]
    for forward_example in range(0, np.shape(test_inputs)[0]):
        Z = []
        for layer in range(0, len(neural_net)):
            # Forward prop
            if (layer == 0):
                activations0[forward_example] = test_inputs[forward_example]
            output_A, output_Z = forward_prop_layer(activations0[forward_example], params_w[layer], params_b[layer])
            activations0[forward_example] = output_A
            Z.append(output_Z)

    activations0 = softmax(activations0)

    error = 0
    for example in range(0, np.shape(test_inputs)[0]):
        # error += -Y[example] * np.log(activations0[example]) - (1 - Y[example]) * np.log(1 - activations0[example])
        error += np.abs(test_outputs[example] - activations0[example])
    return error / np.shape(test_inputs)[0]

def softmax(x):
    temporary = np.copy(x)
    if (temporary.ndim == 2):
        temporary = np.sum(temporary, axis = 1)
        temporary = np.expand_dims(np.exp(temporary), axis = 1)
    else:
        temporary = np.expand_dims(temporary, axis = 1)
        temporary = np.sum(np.exp(temporary), axis = 0)
    return 3 * np.exp(x) / temporary

def gradient_descent(grads_w, grads_b, alpha):
    weight_sum = 0
    for layer in range(0, len(neural_net) - 1):
        weight_sum += np.sum(params_w[layer])
    return params_w - alpha * grads_w - ((lambda_ / np.shape(X)[0]) * weight_sum), params_b - alpha * grads_b
    
X = []
Y = []
test_X = []
test_Y = []

for game_number in range(1, 10000):
    file_name = "games\\" + str(game_number) + ".json"
    print(file_name)
    tempX, tempY = GameParser.populate_inputs(file_name)
    # Only add the game data if the game is valid
    if (tempX is not None):
        X.append(tempX)
        Y.append(tempY)

for game_number in range(10000, 20000):
    file_name = "games\\" + str(game_number) + ".json"
    print(file_name)
    tempX, tempY = GameParser.populate_inputs(file_name)
    # Only add the game data if the game is valid
    if (tempX is not None):
        test_X.append(tempX)
        test_Y.append(tempY)

# Convert X and Y to numpy arrays
X = np.array(X)
Y = np.array(Y)

test_X = np.array(test_X)
test_Y = np.array(test_Y)

# # Generates all combinations of 1s and 0s for input data
# for i in range(0, np.shape(X)[0]):
#     num = i
#     for j in range(0, np.shape(X)[1]):
#         rem = num // (2**(np.shape(X)[1]-1-j))
#         X[i][j] = rem
#         num -= rem * (2**(np.shape(X)[1]-1-j))

# # Generates the correct outputs for the inputs X
# for i in range(0, np.shape(Y)[0]):
#     for j in range(0, 2):
#     # Y[i] = X[i][0] and X[i][1]
#         Y[i][j] = (X[i][0] and X[i][1]) or not(X[i][0] or X[i][1])

neural_net = [{"j": 292, "k": 26},
              {"j": 26, "k": 7}]

# Initialize weights and biases
# params_w, params_b = init_network(neural_net)

# # Load params using previously saves params (optional)
with open('params_w', 'rb') as f:
    params_w = pickle.load(f)
    print(params_w)
with open('params_b', 'rb') as g:
    params_b = pickle.load(g)
    print(params_b)

errors = []
test_errors = []
num_epochs = 20000
learning_rate = 1
lambda_ = 0
num_examples = np.shape(X)[0]

for epoch in range(0, num_epochs):
    print(epoch)
    # Initialize gradients at 0
    grads_w = []
    grads_b = []
    for i in range(len(neural_net) - 1, -1, -1):
        grads_w.insert(0, np.zeros((neural_net[i]["k"], neural_net[i]["j"])))
    for i in range(len(neural_net) - 1, -1, -1):
        grads_b.insert(0, np.zeros((neural_net[i]["k"])))


    RESULT = [None] * num_examples

    # For each example
    for i in range(0, np.shape(X)[0]):
        activations = None
        activations = []
        output_Z = None
        output_A = None
        Z = []
        for layer in range(0, len(neural_net)):
            # Forward prop
            if (layer == 0):
                activations.append(X[i])
            #                                           30,                 2,30            (1, 2)
            output_A, output_Z = forward_prop_layer(activations[layer], params_w[layer], params_b[layer])
            activations.append(output_A)
            Z.append(output_Z)

        # Back prop 
        # BP 1: Compute error_L = dC/dA * sigmoid_derivative(z_L)

        error_last = None
        # error_last = ((-Y[i] / output_A) + (1 - Y[i]) / (1 - output_A)) * sigmoid_derivative(output_Z)
        
        error_last = ((-Y[i] / output_A) + (1 - Y[i]) / (1 - output_A)) * sigmoid_derivative(output_Z)
        
        if (error_last.ndim == 1):
            error_last = np.expand_dims(error_last, axis = 1)
        temp_activations = activations[-2]
        if (activations[-2].ndim == 1):
            temp_activations = np.expand_dims(temp_activations, axis = 1)
        weight_gradient = np.dot(error_last, temp_activations.T)
        grads_w[len(neural_net) - 1] = grads_w[len(neural_net) - 1] + weight_gradient
        error_next = error_last

        for k in range(0, len(grads_b[len(neural_net) - 1])):
            grads_b[len(neural_net) - 1][k] = grads_b[len(neural_net) - 1][k] + error_next[k][0]
        
        # BP 2/3: Backprop the error: For each l from L, L-1, ..., 2, compute error_l = np.dot(weights_l+1.T, error_l+1) * sigmoid_derivative(z_curr)
        for j in range(len(neural_net) - 1, 0, -1):
            # Ensure that error_next is 2 dimensions when passed to error_curr
            if (error_next.ndim == 1):
                temp0 = np.copy(error_next)
                temp0 = np.expand_dims(temp0, axis = 0)
                error_curr = np.dot(temp0, params_w[j]) * sigmoid_derivative(Z[j - 1])
            else:
                #                                  30,2            2,1                   30,
                error_curr = np.multiply(np.dot(params_w[j].T, error_next), np.expand_dims(sigmoid_derivative(Z[j - 1]), axis = 1))
            temp1 = np.copy(activations[j-1])
            if (temp1.ndim < 2):
                temp1 = np.expand_dims(temp1, axis = 0)

            weight_gradient = np.dot(error_curr, temp1)
            grads_w[j-1] = grads_w[j-1] + weight_gradient

            for k in range(0, len(grads_b[j-1])):
                grads_b[j-1][k] = grads_b[j-1][k] + error_curr[k][0]

            error_next = error_curr

        RESULT[i] = output_A

    # Divide gradients by number of examples
    grads_w = np.asarray(grads_w)
    grads_w /= np.shape(X)[0]
    grads_b = np.asarray(grads_b)
    grads_b /= np.shape(X)[0]

    # Perform gradient descent
    params_w, params_b = gradient_descent(grads_w, grads_b, learning_rate)

    # Update error values for graphing
    errors.append(error_function(params_w, params_b, X, Y))
    test_errors.append(error_function(params_w, params_b, test_X, test_Y))

# Save params to files
with open('params_w', 'wb') as f:
  pickle.dump(params_w, f)
with open('params_b', 'wb') as g:
  pickle.dump(params_b, g)

# Training Error
plt.subplot(2,1,1)
plt.plot(errors)
plt.ylabel('Training Error')
plt.xlabel('Epoch')
plt.legend(['1', '2','3', '4', '5', '6', '7'])

# Test Error
plt.subplot(2, 1, 2)
plt.plot(test_errors)
plt.ylabel('Test Error')
plt.xlabel('Epoch')
plt.legend(['1', '2','3', '4', '5', '6', '7'])
plt.show()