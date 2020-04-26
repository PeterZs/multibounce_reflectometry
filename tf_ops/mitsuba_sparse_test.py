# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for custom user ops."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

import tensorflow as tf
#import matplotlib.pyplot as plt
import numpy as np
import mitsuba_sparse_grad
import sys
import json

class MitsubaTest(tf.test.TestCase):
   
  def testBasic(self):
    #library_filename = os.path.join(tf.resource_loader.get_data_files_path(), 'mitsuba_v2_op.so')
    #mitsuba = tf.load_op_library(library_filename)
    mitsuba = tf.load_op_library('./mitsuba_v2_sparse_op.so')
    #print(dir(mitsuba))
    lines = sys.stdin.readlines(); 
    #lines = ["4"];
    print(lines);
    _width = int(lines[0]);
    _height = int(lines[0]);
    depthact = tf.constant(float(lines[1]));
    samplecount = float(lines[2]);

    #self.assertEqual(len(mitsuba.OP_LIST.op), 1)
    self.assertEqual(mitsuba.OP_LIST.op[0].name, 'Mitsuba')
    #print("Sending"); 
    
    #A = tf.constant([0.0,0.5,0.0,0.0])
    
    #alpha = tf.Variable(0.1);
    #weight = tf.Variable(0.9);
    params = tf.Variable([0.1, 0.2, 0.3]);

    _normals = np.concatenate([np.ones((_width, _height, 1)) * 0.6, np.ones((_width, _height, 1)) * 0.6, np.ones((_width, _height, 1)) * 1], axis=2);
    print(_normals.shape);
    normals = tf.Variable(_normals, dtype=tf.float32);
    #normals = tf.Variable(np.ones((10, 10, 3)) * 0.2, dtype=tf.float32);

    depth2 = tf.constant(2.0);
    depth4 = tf.constant(4.0);
    
    # TODO: Uncomment when running with a script.
    

    targetspecs = tf.constant([0.1, 0.1, 0.1]);
    _targetnormals = np.concatenate([np.ones((_width, _height, 1)) * 0.789, np.ones((_width, _height, 1)) * 0.211, np.ones((_width, _height, 1)) * 0.789], axis=2);
    targetnormals = tf.constant(_targetnormals, dtype=tf.float32);

    depthinfty = tf.constant(-1.0);

    scountMain = tf.constant(1024.0);
    scountEst = tf.constant(samplecount);

    print("Creating graph")
    
    I = mitsuba.mitsuba(parameter_map=normals, params=params, depth=depthact, samples=scountEst);
    
    refimg = None;

    print("Running reference graph");
    with self.test_session() as sess:
        ref = mitsuba.mitsuba(parameter_map=targetnormals, params=targetspecs, depth=depthinfty, samples=scountMain);
        refimg = ref.eval();
    
    L = tf.reduce_sum(tf.pow(I - refimg,2));
    #grad_alpha, grad_w = tf.gradients(xs=[alpha, weight], ys=L);
    #optimizer = tf.train.GradientDescentOptimizer(0.0004)
    optimizer = tf.train.AdamOptimizer(0.1)
    train = optimizer.minimize(L, var_list=[normals]);

    #print("Testing Graph")
    #with self.test_session():
    #  self.assertEqual(acop.eval(), b'A(m, 0) == A(m-1, 1)')
    
    # Projective gradient.
    #clipA = alpha.assign(tf.minimum(0.95, tf.maximum(0.05, alpha)));
    #clipW = weight.assign(tf.minimum(0.99, tf.maximum(0.01, weight)));
    #tf.minimum(0.95, 0.99);
    
    #lparams = tf.minimum(0.99, tf.maximum(0.01, params))
    #sparams = lparams[0:-1] 
    #aparams = lparams[-1:] 
    #snparams = sparams / tf.reduce_sum(sparams);
    #clipP = params.assign(tf.concat([snparams, aparams],0));
    
    converted = 2.0 * (normals - 0.5);
    normalized = converted / tf.sqrt(tf.reduce_sum(tf.square(converted), 2, keep_dims=True));
    rgbvals = (normalized / 2) + 0.5;

    projectN = normals.assign(rgbvals);

    clipN = normals.assign(tf.minimum(1.0, tf.maximum(0.0, normals)));
    #clip = tf.group(clipA, clipW);
    
    gerror = tf.reduce_sum(tf.pow(normals - targetnormals, 2));
    #with self.test_session():
    #   self.assertEqual(acop.eval(), b'A(m, 0) == A(m-1, 1)')
    As = [];
    Ws = [];
    Es = [];
    print("####$$####");
    with self.test_session() as sess:
        init = tf.initialize_all_variables()
        sess.run(init)
        for i in range(0,250):
            #init = tf.global_variable_intializer()
            #A = grad_alpha.eval()
            #W = grad_w.eval()
            sess.run(train);
            sess.run(projectN);
            
            arr = sess.run(normals);
            for z in range(3):
                for i in range(_width):
                    for j in range(_height):
                        print(arr[i, j, z], " ", end="", file=sys.stderr);
                    print("", file=sys.stderr);
                print("\n", file=sys.stderr)

            #print(sess.run(normals)[0]);
            print("Error in normals: ",sess.run(gerror), file=sys.stderr);
            print("Error in image: ", sess.run(L), file=sys.stderr);
            
            print(sess.run(L));
            #Es.append(sess.run(L));
            #Ws.append(sess.run(params)[2].tolist());

            #print(A);
            #print(W);
        #plt.gray()
        #plt.imshow(X * 100)
        #plt.show()
        #plt.savefig("/home/sassy/example.tiff")
        #plt.show()
    print("####$$####")

    #x = open("/home/sassy/mtstfrun.dat", 'w');
    #x.write(json.dumps([As, Ws]));
    #x.close();

if __name__ == '__main__':
  tf.test.main()
