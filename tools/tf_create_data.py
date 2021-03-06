import math
import tensorflow as tf
import cv2
import os
from glob import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', required=True,
                    help='input to big size input')
parser.add_argument('--output_dir', required=True,
                    help='output directory for training examples')
parser.add_argument(
    '--strides', default=[100, 100], help='output directory for training examples')
parser.add_argument(
    '--ksize', default=[256, 512], help='output directory for training examples')

args = parser.parse_args()


def extract_patches(image, k_size, strides):
    images = tf.extract_image_patches(tf.expand_dims(
        image, 0), k_size, strides, rates=[1, 1, 1, 1], padding='SAME')[0]
    images_shape = tf.shape(images)
    images_reshape = tf.reshape(
        images, [images_shape[0]*images_shape[1], *k_size[1:3], 3])
    return images_reshape


if __name__ == '__main__':
    os.makedirs(args.output_dir, exist_ok=True)
    paths = glob(args.input_dir+'/*.png')
    path = tf.placeholder(tf.string)
    raw_data = tf.read_file(path)
    image = tf.image.decode_png(raw_data)
    rand = tf.to_int32(tf.to_float(tf.shape(image)[:2]) * tf.random_uniform([], 0.5, 1.5))
    image = tf.image.resize_bilinear(tf.expand_dims(image, 0), rand)[0]
    w = tf.shape(image)[1]
    a, b = image[:, :w//2, :], image[:, w//2:, :]
    k_size = [1, *args.ksize, 1]
    strides = [1, *args.strides, 1]
    patcha = extract_patches(a, k_size, strides)
    patchb = extract_patches(b, k_size, strides)
    output_image = tf.concat([patcha, patchb], axis=2)
    k = 0
    with tf.Session() as sess:
        for p in paths:
            name = p.split('/')[-1].split('.png')[0]
            for _ in range(1):
                rv = sess.run(output_image, {path: p})
                for i, image in enumerate(rv):
                    rgb = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    out_path = '{}/{}.png'.format(args.output_dir, k)
                    cv2.imwrite(out_path, rgb)
                    k += 1
                    print(p, k, end='\r')
                    break
