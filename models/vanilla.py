from __future__ import division

import matplotlib.pyplot as plt
import torch
from torch.autograd import Variable

from base import AbstractController
from networks.feedforward import LinearSimpleStructNetwork
from structs.simple import Stack


class VanillaController(AbstractController):
    """
    A simple Controller that uses a SimpleStruct as its data structure.
    """

    def __init__(self, input_size, read_size, output_size,
                 network_type=LinearSimpleStructNetwork, struct_type=Stack):
        """
        Constructor for the VanillaController object.

        :type input_size: int
        :param input_size: The size of the vectors that will be input to
            this Controller

        :type read_size: int
        :param read_size: The size of the vectors that will be placed on
            the neural data structure

        :type output_size: int
        :param output_size: The size of the vectors that will be output
            from this Controller

        :type struct_type: type
        :param struct_type: The type of neural data structure that this
            Controller will operate

        :type network_type: type
        :param network_type: The type of the Network that will perform
            the neural network computations
        """
        super(VanillaController, self).__init__(read_size, struct_type)
        self._read = None
        self._network = network_type(input_size, read_size, output_size)
        self._input_size = input_size
        self._output_size = output_size
        self._read_size = read_size

        self._buffer_in = None
        self._buffer_out = None

        self._t = 0
        self._zeros = None

    def _init_buffer(self, batch_size, xs):
        """
        Initializes the input and output buffers. The input buffer will
        contain a specified collection of values. The output buffer will
        be empty.

        :type batch_size: int
        :param batch_size: The number of trials in each mini-batch where
            this Controller is used

        :type xs: Variable
        :param xs: An array of values that will be placed on the input
            buffer. The dimensions should be [batch size, t, read size],
            where t is the maximum length of a string represented in xs

        :return: None
        """
        self._buffer_in = xs
        self._buffer_out = []

        self._t = 0
        self._zeros = Variable(torch.zeros(batch_size, self._input_size))

    """ Neural Network Computation """

    def forward(self):
        """
        Computes the output of the neural network given an input. The
        network should push a value onto the neural data structure and
        pop one or more values from the neural data structure, and
        produce an output based on this information and recurrent state
        if available.

        :return: None
        """
        if self._read is None:
            raise RuntimeError("The data structure has not been initialized.")

        x = self._read_input()

        output, (v, u, d) = self._network(x, self._read)
        self._read = self._struct(v, u, d)

        self._write_output(output)

    """ Accessors """

    def _read_input(self):
        """
        Returns the next vector from the input buffer.

        :rtype: Variable
        :return: The next vector from the input buffer
        """
        if self._t < self._buffer_in.size(1):
            self._t += 1
            return self._buffer_in[:, self._t - 1, :]
        else:
            return self._zeros

    def read_output(self):
        """
        Returns the next vector from the output buffer.

        :rtype: Variable
        :return: The next vector from the output buffer
        """
        if len(self._buffer_out) > 0:
            return self._buffer_out.pop(0)
        else:
            return None

    def _write_output(self, value):
        """
        Adds a symbol to the output buffer.

        :type value: Variable
        :param value: The value to add to the output buffer

        :return: None
        """
        self._buffer_out.append(value)

    """ Analytical Tools """

    def trace(self, trace_x):
        """
        Draws a graphic representation of the neural data structure
        instructions produced by the Controller's Network at each time
        step for a single input.

        :type trace_x: Variable
        :param trace_x: An input string

        :return: None
        """
        self.eval()
        self.init_controller(1, trace_x)

        max_length = trace_x.data.shape[1]

        self._network.start_log(max_length)
        for j in xrange(max_length):
            self.forward()
        self._network.stop_log()

        x_labels = ["x_" + str(i) for i in xrange(self._input_size)]
        y_labels = ["y_" + str(i) for i in xrange(self._output_size)]
        i_labels = ["Pop", "Push"]
        v_labels = ["v_" + str(i) for i in xrange(self._read_size)]
        labels = x_labels + y_labels + i_labels + v_labels

        plt.imshow(self._network.log_data, cmap="Greys",
                   interpolation="nearest")
        plt.title("Trace")
        plt.yticks(range(len(labels)), labels)
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.show()
