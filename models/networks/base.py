from abc import ABCMeta, abstractmethod

import numpy as np
import torch.nn as nn
from torch.autograd import Variable


class Network(nn.Module):
    """
    Abstract class for neural network Modules to be used in Controllers.
    Inherit from this class in order to create a custom architecture for
    a Controller, or to create a network compatible with a custom neural
    data structure.
    """
    __metaclass__ = ABCMeta

    def __init__(self, input_size, read_size, output_size):
        """
        Constructor for the Network object.

        :type input_size: int
        :param input_size: The size of input vectors to this Network

        :type read_size: int
        :param read_size: The size of vectors placed on the neural data
            structure

        :type output_size: int
        :param output_size: The size of vectors output from this Network
        """
        super(Network, self).__init__()
        self._input_size = input_size
        self._read_size = read_size
        self._output_size = output_size

    @abstractmethod
    def forward(self, x, r):
        """
        This Network should take an input and the previous item read
        from the neural data structure and produce an output and a set
        of instructions for operating the neural data structure.

        :type x: Variable
        :param x: The input to this Network

        :type r: Variable
        :param r: The previous item read from the neural data structure

        :rtype: tuple
        :return: The first item of the tuple should contain the output
            of the network. The second item should be a tuple containing
            instructions for the neural data structure. For example, the
            return value corresponding to the instructions
                - output y
                - pop a strength u from the data structure
                - push v with strength d to the data structure
            is (y, (v, u, d))
        """
        raise NotImplementedError("Missing implementation for forward")

    @staticmethod
    def init_normal(tensor):
        """
        Populates a Variable with values drawn from a normal
        distribution with mean 0 and standard deviation 1/sqrt(n), where
        n is the length of the Variable.

        :type tensor: Variable
        :param tensor: The Variable to populate with values

        :return: None
        """
        n = tensor.data.shape[0]
        tensor.data.normal_(0, 1. / np.sqrt(n))


class SimpleStructNetwork(Network):
    """
    Abstract class for Networks to be used with SimpleStructs (see
    structs.simple.SimpleStruct). This class primarily contains
    reporting tools that record the SimpleStruct instructions at each
    time step.
    """

    def __init__(self, input_size, read_size, output_size):
        """
        Constructor for the SimpleStructNetwork object. In addition to
        calling the base class constructor, this constructor initializes
        private properties used for reporting. Logged data are stored in
        self._log, a Numpy array whose columns contain the instructions
        computed by the SimpleStructNetwork to the SimpleStruct at each
        time step.

        :type input_size: int
        :param input_size: The size of input vectors to this Network

        :type read_size: int
        :param read_size: The size of vectors placed on the neural data
            structure

        :type output_size: int
        :param output_size: The size of vectors output from this Network
        """
        super(SimpleStructNetwork, self).__init__(input_size, read_size,
                                                  output_size)

        # Initialize reporting tools
        self._log = False  # Whether or not to log data
        self._log_data = None  # A numpy array containing logged data
        self._log_data_size = 0  # The maximum number of entries to log
        self._curr_log_entry = 0  # The number of entries logged already

    """ Reporting """

    def init_log(self, log_data_size):
        """
        Initializes self._log_data to an empty array of a specified
        size.

        :type log_data_size: int
        :param log_data_size: The number of columns of self._log_data
            (i.e., the number of time steps for which data are logged)

        :return: None
        """
        self._log_data = np.zeros([2 + self._read_size, log_data_size])
        self._log_data_size = log_data_size
        self._curr_log_entry = 0
        return

    def start_log(self, log_data_size=None):
        """
        Sets self._log to True, so that data will be logged the next
        time self.forward is called.

        :type log_data_size: int
        :param log_data_size: If a value is supplied for this argument,
            then self.init_log will be called.

        :return: None
        """
        self._log = True
        if log_data_size is not None:
            self.init_log(log_data_size)
        return

    def stop_log(self):
        """
        Sets self._log to False, so that data will no longer be logged
        the next time self.forward is called.

        :return: None
        """
        self._log = False
        return

    def _log(self, v, u, d):
        """
        Records a set of SimpleSet instructions to self._log_data.

        :type v: Variable
        :param v: The value that will be pushed to the data structure

        :type u: Variable
        :param u: The total strength of values that will be popped from
            the data structure

        :type d: Variable
        :param d: The strength with which v will be pushed to the data
            structure

        :return: None
        """
        if not self._log:
            return
        elif self._curr_log_entry >= self._log_data_size:
            return

        self._log_data[2, self._curr_log_entry] = v.data.numpy()
        self._log_data[0, self._curr_log_entry] = u.data.numpy()
        self._log_data[1, self._curr_log_entry] = d.data.numpy()

        self._curr_log_entry += 1

        return
