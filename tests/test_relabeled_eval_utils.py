#!/usr/bin/python3

import numpy as np
import pdb
import torch

from mseg.utils.names_utils import (
    load_class_names,
    get_universal_class_names,
)

from mseg_semantic.utils.transform import ToUniversalLabel
from mseg_semantic.tool.relabeled_eval_utils import (
	eval_rel_model_pred_on_unrel_data
)


def test_eval_relabeled_pair1():
    """
    Person vs. Motorcyclist in center
    Relabeled model correctly predicts `motorcylist`. for `motorcylist`.
    
    Motorcyclist silhouette pattern:
            [0,0,0,0],
            [0,1,1,0],
            [0,1,1,0],
            [0,1,1,0]
    """
    orig_dname = 'coco-panoptic-133'
    relabeled_dname = 'coco-panoptic-133-relabeled'
    original_names = load_class_names(orig_dname)
    relabeled_names = load_class_names(relabeled_dname)
    u_names = get_universal_class_names()

    # prediction in universal taxonomy
    pred_rel = np.ones((4,4), dtype=np.uint8) * u_names.index('sky')
    pred_rel[1:,1:3] = u_names.index('motorcyclist')

    # original COCO image, in coco-panoptic-133
    target_img = np.ones((4,4)) * original_names.index('sky-other-merged')
    target_img[1:,1:3] = original_names.index('person')
    #target_img = target_img.reshape(1,4,4)

    # relabeled COCO image, in coco-panoptic-133-relabeled
    target_img_relabeled = np.ones((4,4)) * relabeled_names.index('sky')
    target_img_relabeled[1:,1:3] = relabeled_names.index('motorcyclist')
    #target_img_relabeled = target_img_relabeled.reshape(1,4,4)

    orig_to_u_transform = ToUniversalLabel(orig_dname)
    relabeled_to_u_transform = ToUniversalLabel(relabeled_dname)
    pred_unrel, target_img = eval_rel_model_pred_on_unrel_data(
        pred_rel,
        target_img,
        target_img_relabeled,
        orig_to_u_transform,
        relabeled_to_u_transform
    )
    # treated as 100% accuracy
    assert np.allclose(pred_unrel, target_img)


def test_eval_relabeled_pair2():
    """
    Person vs. Motorcyclist in center.
    Relabeled model incorrectly predicts `person` instead of `motorcylist`.
    
            [0,0,0,0],
            [0,1,1,0],
            [0,1,1,0],
            [0,1,1,0]
    """
    orig_dname = 'coco-panoptic-133'
    relabeled_dname = 'coco-panoptic-133-relabeled'
    original_names = load_class_names(orig_dname)
    relabeled_names = load_class_names(relabeled_dname)
    u_names = get_universal_class_names()

    pred_rel = np.ones((4,4), dtype=np.uint8) * u_names.index('sky')
    pred_rel[1:,1:3] = u_names.index('person')

    # original COCO image, in coco-panoptic-133
    target_img = np.ones((4,4)) * original_names.index('sky-other-merged')
    target_img[1:,1:3] = original_names.index('person')

    # relabeled COCO image, in coco-panoptic-133-relabeled
    target_img_relabeled = np.ones((4,4)) * relabeled_names.index('sky')
    target_img_relabeled[1:,1:3] = relabeled_names.index('motorcyclist')

    orig_to_u_transform = ToUniversalLabel(orig_dname)
    relabeled_to_u_transform = ToUniversalLabel(relabeled_dname)
    pred_unrel, target_gt_univ = eval_rel_model_pred_on_unrel_data(
        pred_rel,
        target_img,
        target_img_relabeled,
        orig_to_u_transform,
        relabeled_to_u_transform
    )
    # treated as 0% accuracy for person's silhouette and interior

    target_gt = np.ones((4,4), dtype=np.uint8) * u_names.index('sky')
    target_gt[1:,1:3] = u_names.index('person')
    assert np.allclose(target_gt_univ, target_gt)

    IGNORE_IDX = 255 # represents unlabeled
    gt_pred_unrel = np.ones((4,4), dtype=np.uint8) * u_names.index('sky')
    gt_pred_unrel[1:,1:3] = IGNORE_IDX
    assert np.allclose(pred_unrel, gt_pred_unrel)


if __name__ == '__main__':
    """ """
    test_eval_relabeled_pair1()
    test_eval_relabeled_pair2()
