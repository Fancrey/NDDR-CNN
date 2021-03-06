# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Contains model definitions for versions of the Oxford VGG network.

These model definitions were introduced in the following technical report:

  Very Deep Convolutional Networks For Large-Scale Image Recognition
  Karen Simonyan and Andrew Zisserman
  arXiv technical report, 2015
  PDF: http://arxiv.org/pdf/1409.1556.pdf
  ILSVRC 2014 Slides: http://www.robots.ox.ac.uk/~karen/pdf/ILSVRC_2014.pdf
  CC-BY-4.0

More information can be obtained from the VGG website:
www.robots.ox.ac.uk/~vgg/research/very_deep/

Usage:
  with slim.arg_scope(vgg.vgg_arg_scope()):
    outputs, end_points = vgg.vgg_a(inputs)

  with slim.arg_scope(vgg.vgg_arg_scope()):
    outputs, end_points = vgg.vgg_16(inputs)

@@vgg_a
@@vgg_16
@@vgg_19
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

slim = tf.contrib.slim


def vgg_16_deeplab_st(inputs,
           num_classes=21,
           is_training=True,
           dropout_keep_prob=0.5,
           scope='vgg_16'):
  """VGG-16 Deeplab lfov model for single task.

  Args:
    inputs: a tensor of size [batch_size, height, width, channels].
    num_classes: number of predicted classes.
    is_training: whether or not the model is being trained.
    dropout_keep_prob: the probability that activations are kept in the dropout
      layers during training.
    scope: Optional scope for the variables.

  Returns:
    the last op containing the log predictions and end_points dict.
  """
  with tf.variable_scope(scope, 'vgg_16', [inputs]) as sc:
    end_points_collection = sc.name + '_end_points'
    # Collect outputs for conv2d, fully_connected and max_pool2d.
    with slim.arg_scope([slim.conv2d, slim.fully_connected, slim.max_pool2d],
                        outputs_collections=end_points_collection):
      net = slim.repeat(inputs, 2, slim.conv2d, 64, [3, 3], scope='conv1')
      net = slim.max_pool2d(net, [3, 3], stride=2, padding='SAME', scope='pool1')
      net = slim.repeat(net, 2, slim.conv2d, 128, [3, 3], scope='conv2')
      net = slim.max_pool2d(net, [3, 3], stride=2, padding='SAME', scope='pool2')
      net = slim.repeat(net, 3, slim.conv2d, 256, [3, 3], scope='conv3')
      net = slim.max_pool2d(net, [3, 3], stride=2, padding='SAME', scope='pool3')
      net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], scope='conv4')
      net = slim.max_pool2d(net, [3, 3], stride=1, padding='SAME', scope='pool4')
      # net = slim.repeat(net, 3, conv2d_same, 512, [3, 3], stride=1, rate=2, scope='conv5')
      net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], rate=2, scope='conv5')
      net = slim.max_pool2d(net, [3, 3], stride=1, padding='SAME', scope='pool5_max')
      net = slim.avg_pool2d(net, [3, 3], stride=1, padding='SAME', scope='pool5_avg')

      # Use conv2d instead of fully_connected layers.
      rate = 12
      net = slim.conv2d(net, 1024, [3, 3], rate=rate, padding='SAME', scope='fc6')
      net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                            scope='dropout6')
      net = slim.conv2d(net, 1024, [1, 1], padding='SAME', scope='fc7')
      net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                            scope='dropout7')
      net = slim.conv2d(net, num_classes, [1, 1],
                            activation_fn=None,
                            normalizer_fn=None,
                            scope='fc8_voc12')

        

      # Convert end_points_collection into a end_point dict.
      end_points = slim.utils.convert_collection_to_dict(end_points_collection)

  return net, end_points


def vgg_16_shortcut_deeplab_st(inputs,
           num_classes=21,
           is_training=True,
           dropout_keep_prob=0.5,
           scope='vgg_16'):
  """VGG-16 Deeplab lfov model for single task with shortcut connections.

  Args:
    inputs: a tensor of size [batch_size, height, width, channels].
    num_classes: number of predicted classes.
    is_training: whether or not the model is being trained.
    dropout_keep_prob: the probability that activations are kept in the dropout
      layers during training.
    scope: Optional scope for the variables.

  Returns:
    the last op containing the log predictions and end_points dict.
  """
  with tf.variable_scope(scope, 'vgg_16', [inputs]) as sc:
    end_points_collection = sc.name + '_end_points'
    # Collect outputs for conv2d, fully_connected and max_pool2d.
    with slim.arg_scope([slim.conv2d, slim.fully_connected, slim.max_pool2d],
                        outputs_collections=end_points_collection):
      net = slim.repeat(inputs, 2, slim.conv2d, 64, [3, 3], scope='conv1')
      net = slim.max_pool2d(net, [3, 3], stride=2, padding='SAME', scope='pool1')
      pool1_output = net
      net = slim.repeat(net, 2, slim.conv2d, 128, [3, 3], scope='conv2')
      net = slim.max_pool2d(net, [3, 3], stride=2, padding='SAME', scope='pool2')
      pool2_output = net
      net = slim.repeat(net, 3, slim.conv2d, 256, [3, 3], scope='conv3')
      net = slim.max_pool2d(net, [3, 3], stride=2, padding='SAME', scope='pool3')
      pool3_output = net
      net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], scope='conv4')
      net = slim.max_pool2d(net, [3, 3], stride=1, padding='SAME', scope='pool4')
      pool4_output = net
      # net = slim.repeat(net, 3, conv2d_same, 512, [3, 3], stride=1, rate=2, scope='conv5')
      net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], rate=2, scope='conv5')
      net = slim.max_pool2d(net, [3, 3], stride=1, padding='SAME', scope='pool5_max')
      net = slim.avg_pool2d(net, [3, 3], stride=1, padding='SAME', scope='pool5_avg')
      pool5_output = net

      h = tf.shape(pool5_output)[1]
      w = tf.shape(pool5_output)[2]
      pool1_output_resize = tf.image.resize_bilinear(pool1_output, [h, w])
      pool2_output_resize = tf.image.resize_bilinear(pool2_output, [h, w])
      pool3_output_resize = tf.image.resize_bilinear(pool3_output, [h, w])
      pool4_output_resize = tf.image.resize_bilinear(pool4_output, [h, w])

      with slim.arg_scope([slim.conv2d], biases_initializer=tf.zeros_initializer()):
        conv_concat_1 = tf.concat([pool1_output_resize, pool2_output_resize, pool3_output_resize, pool4_output_resize, pool5_output], axis=-1, name='conv_concat')

        d = pool5_output.get_shape().as_list()[-1]
        net = slim.conv2d(conv_concat_1, d, [1, 1], scope='shortcuts')


      # Use conv2d instead of fully_connected layers.
      rate = 12
      net = slim.conv2d(net, 1024, [3, 3], rate=rate, padding='SAME', scope='fc6')
      net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                            scope='dropout6')
      net = slim.conv2d(net, 1024, [1, 1], padding='SAME', scope='fc7')
      net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                            scope='dropout7')
      net = slim.conv2d(net, num_classes, [1, 1],
                            activation_fn=None,
                            normalizer_fn=None,
                            scope='fc8_voc12')

      # Convert end_points_collection into a end_point dict.
      end_points = slim.utils.convert_collection_to_dict(end_points_collection)

  return net, end_points