# derived from label_image.py from
# https://medium.com/@linjunghsuan/create-a-simple-image-classifier-using-tensorflow-a7061635984a
# . At the time of writing that code was unlicensed and not copyrighted. Here's
# mine:

# classify.py - Classify an image with TensorFlow.
# Copyright (C) 2017  Adam Monsen <haircut@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import glob
import sys
import tensorflow as tf

graph_path = 'output_graph.pb'
labels_path = 'output_labels.txt'

parser = argparse.ArgumentParser()
parser.add_argument(
    '--image_dir',
    type=str,
    default='',
    help='Path to dir of images to classify.'
)
args, unparsed = parser.parse_known_args()

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line
    in tf.gfile.GFile(labels_path)]

# Unpersists graph from file
with tf.gfile.FastGFile(graph_path, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')


with tf.Session() as sess:
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    fileList = glob.glob(args.image_dir + '/*')
    fileList.sort()

    for image_path in fileList:
        print "classify {} ...".format(image_path)

        # Read in the image_data
        image_data = tf.gfile.FastGFile(image_path, 'rb').read()

        predictions = sess.run(softmax_tensor, 
        {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            print('%s (score = %.5f)' % (human_string, score))

        print
