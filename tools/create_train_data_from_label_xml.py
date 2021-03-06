import os
from xml_tools import get_box, draw_cell
from glob import glob
import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', default='output/run_method2', help='input')
parser.add_argument('--output_dir', default='output/propose_region', help='input')
parser.add_argument('--output_type', default="input_output", choices=["merge", "input_output"])
args = parser.parse_args()



def create_train_data_from_label_xml(img_paths, xml_paths, output_path):
    dict_boxes = {}
    dict_images = {}
    for path in xml_paths:
        name = path.split('/')[-1].split('.')[0]
        dict_boxes[name] = get_box(path)

    for path in img_paths:
        name = path.split('/')[-1].split('.')[0]
        dict_images[name] = cv2.imread(path)

    os.makedirs(output_path, exist_ok=True)
    for k in dict_images.keys():
        b = draw_cell(dict_images[k], dict_boxes[k], mode='binary')
        a = dict_images[k]
        if args.output_type == "merge":
            sample_inputs_outputs = 0.5*a+0.5*b
        else:        
            sample_inputs_outputs = np.concatenate([a, b], axis=1)
        image_output_path = '{}/{}.png'.format(output_path, k)
        print(image_output_path)
        cv2.imwrite(image_output_path, sample_inputs_outputs)


if __name__ == '__main__':
    xml_paths = glob('{}/*.xml'.format(args.input_dir))
    img_paths = glob('{}/*.png'.format(args.input_dir))
    print('Num of sample:', len(xml_paths))
    create_train_data_from_label_xml(
        img_paths, xml_paths, output_path=args.output_dir)
