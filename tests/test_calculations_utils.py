import unittest
import numpy as np
from optimed.wrappers.calculations import (
    cupy_available,
    scipy_label,
    scipy_binary_dilation,
    scipy_distance_transform_edt,
    scipy_minimum,
    scipy_sum,
    filter_mask
)

class TestArrayFunctions(unittest.TestCase):

    # ---------------------------
    # Tests for scipy_label
    # ---------------------------
    def test_scipy_label_cpu(self):
        input_array = np.array([
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=bool)

        labeled, num_labels = scipy_label(input_array, use_gpu=False)
        self.assertEqual(num_labels, 3, f"Expected 3 labels, got {num_labels}")

    @unittest.skipUnless(cupy_available, "cupy not installed. Skipping GPU test for scipy_label.")
    def test_scipy_label_gpu(self):
        input_array = np.array([
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=bool)

        labeled, num_labels = scipy_label(input_array, use_gpu=True)
        self.assertEqual(num_labels, 3, f"GPU: Expected 3 labels, got {num_labels}")

    # ---------------------------
    # Tests for scipy_binary_dilation
    # ---------------------------
    def test_scipy_binary_dilation_cpu(self):
        input_array = np.zeros((5, 5), dtype=bool)
        input_array[2, 2] = True  # center pixel True
        structure = np.ones((3, 3), dtype=bool)

        dilated = scipy_binary_dilation(input_array, structure=structure, iterations=1, use_gpu=False)
        expected = np.zeros((5, 5), dtype=bool)
        expected[1:4, 1:4] = True
        self.assertTrue(np.array_equal(dilated, expected), "CPU binary_dilation did not match expected 3x3 block.")

    @unittest.skipUnless(cupy_available, "cupy not installed. Skipping GPU test for scipy_binary_dilation.")
    def test_scipy_binary_dilation_gpu(self):
        input_array = np.zeros((5, 5), dtype=bool)
        input_array[2, 2] = True
        structure = np.ones((3, 3), dtype=bool)

        dilated = scipy_binary_dilation(input_array, structure=structure, iterations=1, use_gpu=True)
        expected = np.zeros((5, 5), dtype=bool)
        expected[1:4, 1:4] = True
        self.assertTrue(np.array_equal(dilated, expected), "GPU binary_dilation did not match expected 3x3 block.")

    # ---------------------------
    # Tests for scipy_distance_transform_edt
    # ---------------------------
    def test_scipy_distance_transform_edt_cpu(self):
        """
        Note: To compute the distance from every pixel to the nearest True pixel,
        we invert the input. (The EDT function computes distances for zero elements.)
        """
        input_array = np.zeros((5, 5), dtype=bool)
        input_array[2, :] = True  # middle row True
        input_array[:, 2] = True  # middle column True

        # Invert the array so that originally True pixels become False.
        dist_trans = scipy_distance_transform_edt(~input_array, use_gpu=False)
        # Now, for the top-left corner (0,0), the nearest originally True pixel is at (0,2) or (2,0): distance = 2.
        self.assertAlmostEqual(dist_trans[0, 0], 2.0, places=3)
        # The pixel that was originally True (e.g. at (2,2)) now becomes False in the inverted image
        # but its nearest original True (which is now a zero in ~input_array) is itself.
        self.assertAlmostEqual(dist_trans[2, 2], 0.0, places=3, msg="Center point distance should be 0.")

    @unittest.skipUnless(cupy_available, "cupy not installed. Skipping GPU test for scipy_distance_transform_edt.")
    def test_scipy_distance_transform_edt_gpu(self):
        input_array = np.zeros((5, 5), dtype=bool)
        input_array[2, :] = True
        input_array[:, 2] = True

        dist_trans = scipy_distance_transform_edt(~input_array, use_gpu=True)
        self.assertAlmostEqual(dist_trans[0, 0], 2.0, places=3)
        self.assertAlmostEqual(dist_trans[2, 2], 0.0, places=3)

    # ---------------------------
    # Tests for scipy_minimum
    # ---------------------------
    def test_scipy_minimum_cpu(self):
        input_array = np.array([
            [3, 4, 5],
            [7, 1, 2],
            [9, 8, 6]
        ], dtype=np.int32)
        label_array = np.array([
            [1, 1, 2],
            [1, 1, 2],
            [2, 2, 2]
        ], dtype=np.int32)
        min_val_region1 = scipy_minimum(input_array, label_array, 1, use_gpu=False)
        min_val_region2 = scipy_minimum(input_array, label_array, 2, use_gpu=False)
        self.assertEqual(min_val_region1, 1, f"Expected min of 1 for region 1, got {min_val_region1}")
        self.assertEqual(min_val_region2, 2, f"Expected min of 2 for region 2, got {min_val_region2}")

    @unittest.skipUnless(cupy_available, "cupy not installed. Skipping GPU test for scipy_minimum.")
    def test_scipy_minimum_gpu(self):
        input_array = np.array([
            [3, 4, 5],
            [7, 1, 2],
            [9, 8, 6]
        ], dtype=np.int32)
        label_array = np.array([
            [1, 1, 2],
            [1, 1, 2],
            [2, 2, 2]
        ], dtype=np.int32)
        min_val_region1 = scipy_minimum(input_array, label_array, 1, use_gpu=True)
        min_val_region2 = scipy_minimum(input_array, label_array, 2, use_gpu=True)
        self.assertEqual(min_val_region1, 1)
        self.assertEqual(min_val_region2, 2)

    # ---------------------------
    # Tests for scipy_sum
    # ---------------------------
    def test_scipy_sum_cpu(self):
        input_array = np.array([
            [3, 4, 5],
            [7, 1, 2],
            [9, 8, 6]
        ], dtype=np.int32)
        label_array = np.array([
            [1, 1, 2],
            [1, 1, 2],
            [2, 2, 2]
        ], dtype=np.int32)
        sum_val_region1 = scipy_sum(input_array, label_array, 1, use_gpu=False)
        sum_val_region2 = scipy_sum(input_array, label_array, 2, use_gpu=False)
        self.assertEqual(sum_val_region1, 15, f"Expected sum of 15 for region 1, got {sum_val_region1}")
        self.assertEqual(sum_val_region2, 30, f"Expected sum of 30 for region 2, got {sum_val_region2}")

    @unittest.skipUnless(cupy_available, "cupy not installed. Skipping GPU test for scipy_sum.")
    def test_scipy_sum_gpu(self):
        input_array = np.array([
            [3, 4, 5],
            [7, 1, 2],
            [9, 8, 6]
        ], dtype=np.int32)
        label_array = np.array([
            [1, 1, 2],
            [1, 1, 2],
            [2, 2, 2]
        ], dtype=np.int32)
        sum_val_region1 = scipy_sum(input_array, label_array, 1, use_gpu=True)
        sum_val_region2 = scipy_sum(input_array, label_array, 2, use_gpu=True)
        self.assertEqual(sum_val_region1, 15)
        self.assertEqual(sum_val_region2, 30)

    # ---------------------------
    # Tests for filter_mask
    # ---------------------------
    def test_filter_mask_cpu(self):
        mask = np.array([
            [0, 1, 2],
            [3, 0, 4],
            [5, 1, 1]
        ], dtype=np.int32)
        lbls_to_keep = [1, 5]
        filtered = filter_mask(mask, lbls_to_keep, use_gpu=False)
        expected = np.array([
            [0, 1, 0],
            [0, 0, 0],
            [5, 1, 1]
        ], dtype=np.int32)
        self.assertTrue(np.array_equal(filtered, expected), "filter_mask CPU result is incorrect.")

    @unittest.skipUnless(cupy_available, "cupy not installed. Skipping GPU test for filter_mask.")
    def test_filter_mask_gpu(self):
        mask = np.array([
            [0, 1, 2],
            [3, 0, 4],
            [5, 1, 1]
        ], dtype=np.int32)
        lbls_to_keep = [1, 5]
        filtered = filter_mask(mask, lbls_to_keep, use_gpu=True)
        expected = np.array([
            [0, 1, 0],
            [0, 0, 0],
            [5, 1, 1]
        ], dtype=np.int32)
        self.assertTrue(np.array_equal(filtered, expected), "filter_mask GPU result is incorrect.")


if __name__ == '__main__':
    unittest.main()
