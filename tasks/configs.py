""" Defines Task parameters for notable experiment configurations.

The values in a config dictionary are used to populate the parameters of a Task constructor.

Example usage:
  CFGTask(**tasks.configs.dyck_config).run_experiment()

"""

from formalisms.cfg import *
from models.networks.recurrent import LSTMSimpleStructNetwork, RNNSimpleStructNetwork

dyck_config = {
    "grammar": dyck_grammar,
    "to_predict": [u")", u"]"],
    "sample_depth": 5,
}


reverse_config = {
    "grammar": reverse_grammar,
    "to_predict": [u"a1", u"b1"],
    "sample_depth": 12,
}

reverse_RNN = {
    "network_type": RNNSimpleStructNetwork,
    "learning_rate": 0.01,
    "epochs": 100
}

reverse_LSTM = {
    "network_type": LSTMSimpleStructNetwork,
    "learning_rate": 0.01,
    "epochs": 100
}

agreement_config = {
    "grammar": agreement_grammar,
    "to_predict": [u"Auxsing", u"Auxplur"],
    "sample_depth": 8,
}
