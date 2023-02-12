from typing import Tuple
import torch

# BGR
mean = (89.12, 95.82, 93.76)
std = (46.42, 46.20, 50.23)


def test_aug():
    """ used for test"""
    return Normalize(mean=mean, std=std)

class Normalize:
    """ mean and std need order (B, G, R) """
    def __init__(self, mean: Tuple, std: Tuple, mode="mean_std"):
        assert len(mean) == len(std), \
            f"Preprocessing Normalise expects same-size mean and std, got {len(mean)} and {len(std)}"
        self.mean = mean
        self.std = std
        assert mode in ["mean_std", "simple"]
        self.mode = mode

    def __call__(self, image):
        """
        Notes:
            image: (height, width, 3)  numpy.array
        Returns:
            image: (3, height, width)  torch.Tensor
        """
        image = torch.Tensor(image)
        for i in range(len(self.mean)):
            image[:, :, i] = (image[:, :, i] - self.mean[i]) / self.std[i]
        image = image.permute(2, 0, 1)
        return image
