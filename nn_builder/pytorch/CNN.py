import torch
import random
import numpy as np
import torch.nn as nn
from nn_builder.pytorch.Base_Network import Base_Network


class CNN(nn.Module, Base_Network):
    """Creates a PyTorch convolutional neural network
    Args:
        - input_dim: Integer to indicate the number of input channels into the network. e.g. if image is RGB then this should be 3
        - hidden_layers_info: List of layer specifications to specify the hidden layers of the network. Each element of the list must be
                         one of these 6 forms:
                         - ["conv", channels, kernel_size, stride, padding]
                         - ["maxpool", kernel_size, stride, padding]
                         - ["avgpool", kernel_size, stride, padding]
                         - ["adaptivemaxpool", output height, output width]
                         - ["adaptiveavgpool", output height, output width]
                         - ["linear", in, out]
        - output_dim: Integer to indicate the dimension of the output of the network if you want 1 output head. Provide a list of integers
                      if you want multiple output heads
        - output_activation: String to indicate the activation function you want the output to go through. Provide a list of
                             strings if you want multiple output heads
        - hidden_activations: String or list of string to indicate the activations you want used on the output of hidden layers
                              (not including the output layer). Default is ReLU.
        - dropout: Float to indicate what dropout probability you want applied after each hidden layer
        - initialiser: String to indicate which initialiser you want used to initialise all the parameters. All PyTorch
                       initialisers are supported. PyTorch's default initialisation is the default.
        - batch_norm: Boolean to indicate whether you want batch norm applied to the output of every hidden layer. Default is False
        - columns_of_data_to_be_embedded: List to indicate the columns numbers of the data that you want to be put through an embedding layer
                                          before being fed through the other layers of the network. Default option is no embeddings
        - embedding_dimensions: If you have categorical variables you want embedded before flowing through the network then
                                you specify the embedding dimensions here with a list like so: [ [embedding_input_dim_1, embedding_output_dim_1],
                                [embedding_input_dim_2, embedding_output_dim_2] ...]. Default is no embeddings
        - y_range: Tuple of float or integers of the form (y_lower, y_upper) indicating the range you want to restrict the
                   output values to in regression tasks. Default is no range restriction
        - print_model_summary: Boolean to indicate whether you want a model summary printed after model is created. Default is False.
    """

    def __init__(self, hidden_layers_info, output_dim, input_dim=1, output_activation=None, hidden_activations="relu",
                 dropout: float = 0.0, initialiser: str = "default", batch_norm: bool = False, y_range: tuple = (),
                 random_seed=0, print_model_summary: bool =False):
        nn.Module.__init__(self)
        self.valid_cnn_hidden_layer_types = {'conv', 'maxpool', 'avgpool', 'adaptivemaxpool', 'adaptiveavgpool', 'linear'}
        Base_Network.__init__(self, input_dim, hidden_layers_info, output_dim, output_activation,
                              hidden_activations, dropout, initialiser, batch_norm, y_range, random_seed,
                              print_model_summary)

    def check_all_user_inputs_valid(self):
        """Checks that all the user inputs were valid"""
        self.check_input_dim_valid()
        self.check_output_dim_valid()
        self.check_cnn_hidden_layers_valid()
        self.check_activations_valid()
        self.check_initialiser_valid()
        self.check_y_range_values_valid()

    # - ["conv", channels, kernel_size, stride, padding]
    # - ["maxpool", kernel_size, stride, padding]
    # - ["avgpool", kernel_size, stride, padding]
    # - ["adaptivemaxpool", output height, output width]
    # - ["adaptiveavgpool", output height, output width]
    # - ["linear", in, out]

    def create_hidden_layers(self):
        """Creates the linear layers in the network"""
        cnn_hidden_layers = nn.ModuleList([])
        in_channels = self.input_dim
        for layer in self.hidden_layers_info:
            layer_name = layer[0].lower()
            assert layer_name in self.valid_cnn_hidden_layer_types, "Layer name {} not valid, use one of {}".format(layer_name, self.valid_cnn_hidden_layer_types)
            if layer_name == "conv":
                cnn_hidden_layers.extend([nn.Conv2d(in_channels=in_channels, out_channels=layer[1], kernel_size=layer[2],
                                             stride=layer[3], padding=layer[4])])
                in_channels = layer[1]
            elif layer_name == "maxpool":
                cnn_hidden_layers.extend([nn.MaxPool2d(kernel_size=layer[1],
                                             stride=layer[2], padding=layer[3])])
            elif layer_name == "avgpool":
                cnn_hidden_layers.extend([nn.AvgPool2d(kernel_size=layer[1],
                                             stride=layer[2], padding=layer[3])])
            elif layer_name == "adaptivemaxpool":
                cnn_hidden_layers.extend([nn.AdaptiveMaxPool2d(output_size=(layer[1], layer[2]))])
            elif layer_name == "adaptiveavgpool":
                cnn_hidden_layers.extend([nn.AdaptiveAvgPool2d(output_size=(layer[1], layer[2]))])
            elif layer_name == "linear":
                cnn_hidden_layers.extend([nn.Linear(in_features=layer[1], out_features=layer[2])])
            else:
                raise ValueError("Wrong layer name")
        return cnn_hidden_layers

    def create_output_layers(self):
        """Creates the output layers in the network"""
        output_layers = nn.ModuleList([])
        if self.hidden_layers_info[-1][0].lower() in ["adaptivemaxpool", "adaptiveavgpool"]:
            input_dim = self.hidden_layers[-1].output_size[0] * self.hidden_layers[-1].output_size[1]
        elif self.hidden_layers_info[-1][0].lower() == "linear":
            input_dim = self.hidden_layers[-1].out_features
        else:
            raise ValueError("Don't know dimensions for output layer. Must use adaptivemaxpool, adaptiveavgpool, or linear as final output layer")
        if not isinstance(self.output_dim, list): self.output_dim = [self.output_dim]
        for output_dim in self.output_dim:
            output_layers.extend([nn.Linear(input_dim, output_dim)])
        return output_layers

    def initialise_all_parameters(self):
        """Initialises the parameters in the linear and embedding layers"""
        self.initialise_parameters(self.hidden_layers)
        self.initialise_parameters(self.output_layers)

    #
    #

    def forward(self, x):
        pass

