from PIL import Image
from datasets import load_dataset
from matplotlib import pyplot as plt
from vit import ViT
import numpy as np
import os
import requests
import torch as T
from torch.nn import functional as F
import transformers
from torchvision import transforms
import torchvision as tv

# T.manual_seed(1)
T.seed()

T.backends.cudnn.benchmark = True
T.autograd.set_detect_anomaly(True)
T.backends.cuda.matmul.allow_tf32 = True
T.backends.cudnn.allow_tf32 = True

dtype = T.bfloat16
device = "cuda" if T.cuda.is_available() else "cpu"

T.cuda.empty_cache()

vit = ViT(dtype=dtype, device=device)
vit.eval()
if os.path.isfile(vit.file):
    print("Loading model", vit.file)
    vit.load()

proc = transforms.Compose(
    [
        transforms.Resize([512, 512], antialias=True),
        transforms.Lambda(lambda x: x if x.mode == "RGB" else x.convert("RGB")),
        transforms.ToTensor(),
        transforms.ConvertImageDtype(T.bfloat16),
    ]
)

dataset = tv.datasets.INaturalist(
    "./data/",
    version="2021_train_mini",
    target_type="class",
    transform=proc,
    # download=True,
)

im = dataset[1][0].to(dtype=dtype, device=device)

im_m, _ = vit.mask(im.unsqueeze(0), mask=True)
im_r, _ = vit(im_m)

im_m = im_m.squeeze(0)
im_r = im_r.squeeze(0)

# print(im_ex.dtype, im_re.dtype)
# print(im_ex.mean(), im_ex.std(), im_re.mean(), im_re.std())

plt.matshow(im_m.permute([1, 2, 0]).to(dtype=T.float32, device="cpu"))
plt.matshow(im_r.permute([1, 2, 0]).to(dtype=T.float32, device="cpu").detach())
plt.show()
