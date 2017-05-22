#!/usr/bin/env python3
"""Contains the TensorFlow call for the training."""

import sys
import numpy as np
import tensorflow as tf
import salearner.utils as utils

class SALearner:
    """Take care of building TF graph and run the training."""

    def __init__(self, data, learning_rate):
        # extract data
        # TODO rename filename to filenames
        self.filenames = data['filename']
        # TODO rename messageid to messageids
        self.messageids = data['messageid']
        # TODO check the names hot-ones
        self.dataset = data['hot-ones'].astype(np.float32)
        # TODO return a real column vector on importer
        self.labels = data['labels'][:, np.newaxis].astype(np.float32)
        # description variables
        self.nb_ind = data['hot-ones'].shape[0]
        self.ind_size = data['hot-ones'].shape[1]
        # graph actions
        self.tf_init = None
        self.tf_cost_function = None
        self.tf_train_step = None
        # Variables learned
        self.tf_weights = None
        self.tf_bias = None
        # Hyperparameters
        self.learning_rate = learning_rate
        # Training stats
        self.cost_data = utils.MAAcumulator(1)
        self.accuracy_data = utils.MAAcumulator(1)
        # Results
        self.__weights = None
        self.__bias = None
        self.tf_regu = None
        self.tf_accuracy = None
        self.tf_tp = None
        self.tf_tn = None
        self.tf_fp = None
        self.tf_fn = None

    def init_graph(self):
        """Initialize TF compute graph."""
        tf.reset_default_graph()
        # data
        tf_data = tf.placeholder(tf.float32, name='data')
        tf_labels = tf.placeholder(tf.float32, name='labels')
        # weights and bias
        self.tf_weights = tf.Variable(tf.truncated_normal([self.ind_size, 1]))
        self.tf_bias = tf.Variable(tf.zeros([1, 1]))
        # Compute the unit unit
        tf_z = tf.matmul(tf_data, self.tf_weights) + self.tf_bias #z.shape -> [ind_size,1]
        tf_h = tf.sigmoid(tf_z)

        self.tf_regu = tf.reduce_mean(tf.multiply(self.tf_weights, self.tf_weights)) * 1e-7
        self.tf_cost_function = \
            tf.reduce_mean(tf_labels * -tf.log(tf.clip_by_value(tf_h, 1e-10, 1)) + \
                    (1 - tf_labels) * -tf.log(tf.clip_by_value(1 - tf_h, 1e-10, 1))) + \
            self.tf_regu
        # accuracy & details
        tf_decision_vector = tf.round(tf_h)
        tf_correct_prediction = tf.equal(tf_labels, tf_decision_vector)
        self.tf_accuracy = tf.reduce_mean(tf.cast(tf_correct_prediction, tf.float32)) * 100
        # True positive
        self.tf_tp = tf.reduce_mean(
            tf.cast(
                tf.logical_and(
                    tf.cast(tf_decision_vector, tf.bool),
                    tf.cast(tf_labels, tf.bool)), tf.float32)) * 100
        # True negative
        self.tf_tn = tf.reduce_mean(
            tf.cast(
                tf.logical_not(
                    tf.logical_or(
                        tf.cast(tf_decision_vector, tf.bool),
                        tf.cast(tf_labels, tf.bool))), tf.float32)) * 100
        # false negative
        self.tf_fn = tf.reduce_mean(
            tf.cast(
                tf.logical_and(
                    tf.cast(tf_decision_vector, tf.bool),
                    tf.logical_not(
                        tf.cast(tf_labels, tf.bool))),
                tf.float32)) * 100
        # false positive (baad)
        self.tf_fp = tf.reduce_mean(
            tf.cast(
                tf.logical_and(
                    tf.logical_not(
                        tf.cast(tf_decision_vector, tf.bool)),
                    tf.cast(tf_labels, tf.bool)),
                tf.float32)) * 100
        # GD
        self.tf_train_step = tf.train.GradientDescentOptimizer(
            self.learning_rate).minimize(self.tf_cost_function)

        self.tf_init = tf.global_variables_initializer()

    def learn(self, nb_cycle, info_every_cycle, quiet=False):
        """Run the training loop."""
        sess = tf.Session()
        sess.run(self.tf_init)
        # reset accumulators
        self.cost_data.reset()
        self.accuracy_data.reset()
        # get placeholders
        tf_data = tf.get_default_graph().get_tensor_by_name('data:0')
        tf_labels = tf.get_default_graph().get_tensor_by_name('labels:0')


        for cycle in range(nb_cycle):
            _, cost, acc, weights, bias, tp, tn, fp, fn, regu = \
                sess.run([self.tf_train_step, self.tf_cost_function,
                          self.tf_accuracy, self.tf_weights,
                          self.tf_bias,
                          self.tf_tp, self.tf_tn,
                          self.tf_fp, self.tf_fn, self.tf_regu],
                         feed_dict={tf_data: self.dataset,
                                    tf_labels: self.labels})
            # data accumulation
            self.cost_data.add(cost)
            self.accuracy_data.add(acc)
            # results
            self.__weights = weights
            self.__bias = bias
            # Console printing
            if (cycle+1) % info_every_cycle == 0 and not quiet:
                print('-' * 10)
                print('cycle: {}'.format(cycle))
                print('cost: {}'.format(cost))
                print('regu: {}'.format(regu))
                print('accuracy: {}%'.format(acc))
                print('true positive: {}%'.format(tp))
                print('true negative: {}%'.format(tn))
                print('false positive: {}%'.format(fp))
                print('false negative: {}%'.format(fn))
                sys.stdout.flush()

    @property
    def results(self):
        """Return the learned weights/score and bias/threshold."""
        return {'weights': self.__weights,
                'bias': self.__bias}
