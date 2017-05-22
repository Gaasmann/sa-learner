#!/usr/local/env python3
"""Take care of generating SA user_prefs file."""

class ConfigGenerator(object):
    """Take care of generating SA user_prefs file."""
    def __init__(self, rules_list, weights, bias):
        self.rules_list = rules_list
        self.weights = weights
        self.bias = bias
        self.generated_config = None

    def get_config(self):
        """Returns the SA user_prefs config file contents."""
        if not self.generated_config:
            self._generate_config()
        return self.generated_config

    def _generate_config(self):
        if len(self.rules_list) != len(self.weights):
            raise Exception("weights != rules_list")
        self.generated_config = ""
        # bias
        self.generated_config += \
                "required_score {:.2f}\n\n".format(-self.bias)
        # rules
        for idx, rule in enumerate(self.rules_list):
            self.generated_config += \
                "score {} {:.2f}\n".format(rule, self.weights[idx, 0])
