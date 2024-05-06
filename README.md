# RAD-NeRF: Real-time Neural Talking Portrait Synthesis

This repository contains a PyTorch re-implementation of the paper: [Real-time Neural Radiance Talking Portrait Synthesis via Audio-spatial Decomposition](https://arxiv.org/abs/2211.12368).

Before running the reference, we have to install Cuda 12.2 and the similar pytorch version. Simmial versions are very important because separate versions may cause errors due to version incompatibilty

Colab notebook demonstration: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1FCnFrlUllpp54zHQIzHUqp22wd1o1hrV)

### [Github Project Page](https://github.com/shubh0125/RAD-NeRF-Project) | [Paper](https://arxiv.org/abs/2211.12368) |

The Data for the Project can be seen on the link below
### [Drive]()

----
References for the Colab Notebook 

https://colab.research.google.com/github/matsuren/nerf_jax_flax_practice/blob/master/nerf_run.ipynb

https://colab.research.google.com/github/keras-team/keras-io/blob/master/examples/vision/ipynb/nerf.ipynb

-------

The GUI below Can be used for Visualization:

https://user-images.githubusercontent.com/25863658/201629660-7ada624b-8602-4cfe-96b3-61e3d465ced6.mp4

------
# Install

This installation has been tested on the following 
1. Ubuntu 22.04
2. Pytorch 1.12 
3. CUDA 11.6.

```bash
git clone https://github.com/ashawkey/RAD-NeRF.git
cd RAD-NeRF
```

### Install dependency
```bash
# for ubuntu, portaudio is needed for pyaudio to work.
sudo apt install portaudio19-dev

pip install -r requirements.txt
```

### Build extension (optional)
We use [`load`](https://pytorch.org/docs/stable/cpp_extension.html#torch.utils.cpp_extension.load) to build the extension at runtime.
Which may be inconvenient sometimes.
Therefore, we also provide the `setup.py` to build each extension:
```bash
# install all extension modules
bash scripts/install_ext.sh
```

# Data pre-processing

### Preparation:

```bash
## install pytorch3d
pip install "git+https://github.com/facebookresearch/pytorch3d.git"

## prepare face-parsing model
wget https://github.com/YudongGuo/AD-NeRF/blob/master/data_util/face_parsing/79999_iter.pth?raw=true -O data_utils/face_parsing/79999_iter.pth

## prepare basel face model
# 1. download `01_MorphableModel.mat` from https://faces.dmi.unibas.ch/bfm/main.php?nav=1-2&id=downloads and put it under `data_utils/face_tracking/3DMM/`
# 2. download other necessary files from AD-NeRF's repository:
wget https://github.com/YudongGuo/AD-NeRF/blob/master/data_util/face_tracking/3DMM/exp_info.npy?raw=true -O data_utils/face_tracking/3DMM/exp_info.npy
wget https://github.com/YudongGuo/AD-NeRF/blob/master/data_util/face_tracking/3DMM/keys_info.npy?raw=true -O data_utils/face_tracking/3DMM/keys_info.npy
wget https://github.com/YudongGuo/AD-NeRF/blob/master/data_util/face_tracking/3DMM/sub_mesh.obj?raw=true -O data_utils/face_tracking/3DMM/sub_mesh.obj
wget https://github.com/YudongGuo/AD-NeRF/blob/master/data_util/face_tracking/3DMM/topology_info.npy?raw=true -O data_utils/face_tracking/3DMM/topology_info.npy
# 3. run convert_BFM.py
cd data_utils/face_tracking
python convert_BFM.py
cd ../..

## prepare ASR model
# if you want to use DeepSpeech as AD-NeRF, you should install tensorflow 1.15 manually.
# else, we also support Wav2Vec in PyTorch.
```

### Pre-processing Custom Training Video
* Put the training video under `data/<ID>/<ID>.mp4`.

    The video **must be 25FPS, with all frames containing the talking person**. 
    The resolution should be about 512x512, and duration about 1-5min.
    ```bash
    # an example training video from AD-NeRF
    mkdir -p data/obama
    wget https://github.com/YudongGuo/AD-NeRF/blob/master/dataset/vids/Obama.mp4?raw=true -O data/obama/obama.mp4
    ```

* Run script (may take hours and the time depends on the video link)
    ```bash
    # run all steps
    python data_utils/process.py data/<ID>/<ID>.mp4

    # if you want to run a specific step 
    python data_utils/process.py data/<ID>/<ID>.mp4 --task 1 # extract audio wave
    ```

* File structure after finishing all steps:
    ```bash
    ./data/<ID>
    ├──<ID>.mp4 # original video
    ├──ori_imgs # original images from video
    │  ├──0.jpg
    │  ├──0.lms # 2D landmarks
    │  ├──...
    ├──gt_imgs # ground truth images (static background)
    │  ├──0.jpg
    │  ├──...
    ├──parsing # semantic segmentation
    │  ├──0.png
    │  ├──...
    ├──torso_imgs # inpainted torso images
    │  ├──0.png
    │  ├──...
    ├──aud.wav # original audio 
    ├──aud_eo.npy # audio features (wav2vec)
    ├──aud.npy # audio features (deepspeech)
    ├──bc.jpg # default background
    ├──track_params.pt # raw head tracking results
    ├──transforms_train.json # head poses (train split)
    ├──transforms_val.json # head poses (test split)
    ```

# Usage

### Start

We provide some pretrained models [here]("") for quick testing on arbitrary audio.

* Download a pretrained model.
    For example, we download `obama_eo.pth` to `./pretrained/obama_eo.pth`

* Download a pose sequence file.
    For example, we download `obama.json` to `./data/obama.json`

* Prepare your audio as `<name>.wav`, and extract audio features.
    ```bash
    # if model is `<ID>_eo.pth`, it uses wav2vec features
    python nerf/asr.py --wav data/<name>.wav --save_feats # save to data/<name>_eo.npy

    # if model is `<ID>.pth`, it uses deepspeech features 
    python data_utils/deepspeech_features/extract_ds_features.py --input data/<name>.wav # save to data/<name>.npy
    ```
    You can download pre-processed audio features too. 
    For example, we download `intro_eo.npy` to `./data/intro_eo.npy`.

* Run inference:
    It takes about 2GB GPU memory to run inference at 40FPS (measured on a V100).
    ```bash
    # save video to trail_obama/results/*.mp4
    # if model is `<ID>.pth`, should append `--asr_model deepspeech` and use `--aud intro.npy` instead.
    python test.py --pose data/obama.json --ckpt pretrained/obama_eo.pth --aud data/intro_eo.npy --workspace trial_obama/ -O --torso

    # provide a background image (default is white)
    python test.py --pose data/obama.json --ckpt pretrained/obama_eo.pth --aud data/intro_eo.npy --workspace trial_obama/ -O --torso --bg_img data/bg.jpg

    # test with GUI
    python test.py --pose data/obama.json --ckpt pretrained/obama_eo.pth --aud data/intro_eo.npy --workspace trial_obama/ -O --torso --bg_img data/bg.jpg --gui
    ```

### Detailed Usage

When we are running it for the first time it might take some time for the CUDA extensions to load

```bash
# train (head)
# by default, we load data from disk on the fly.
# we can also preload all data to CPU/GPU for faster training, but this is very memory-hungry for large datasets.
# `--preload 0`: load from disk (default, slower).
# `--preload 1`: load to CPU, requires ~70G CPU memory (slightly slower)
# `--preload 2`: load to GPU, requires ~24G GPU memory (fast)
python main.py data/obama/ --workspace trial_obama/ -O --iters 200000

# train (finetune lips for another 50000 steps, run after the above command!)
python main.py data/obama/ --workspace trial_obama/ -O --iters 250000 --finetune_lips

# train (torso)
# <head>.pth should be the latest checkpoint in trial_obama
python main.py data/obama/ --workspace trial_obama_torso/ -O --torso --head_ckpt <head>.pth --iters 200000

# test on the test split
python main.py data/obama/ --workspace trial_obama/ -O --test # use head checkpoint, will load GT torso
python main.py data/obama/ --workspace trial_obama_torso/ -O --torso --test

# test with GUI
python main.py data/obama/ --workspace trial_obama_torso/ -O --torso --test --gui

# test with GUI (load speech recognition model for real-time application)
python main.py data/obama/ --workspace trial_obama_torso/ -O --torso --test --gui --asr

# test with specific audio & pose sequence
# --test_train: use train split for testing
# --data_range: use this range's pose & eye sequence (if shorter than audio, automatically mirror and repeat)
python main.py data/obama/ --workspace trial_obama_torso/ -O --torso --test --test_train --data_range 0 100 --aud data/intro_eo.npy
```

check the `scripts` directory for more provided examples.


# Acknowledgement

* The data pre-processing part is adapted from [AD-NeRF](https://github.com/YudongGuo/AD-NeRF).
* The NeRF framework is based on [torch-ngp](https://github.com/ashawkey/torch-ngp).
* The GUI is developed with [DearPyGui](https://github.com/hoffstadt/DearPyGui).

# Citation

```
@article{tang2022radnerf,
  title={Real-time Neural Radiance Talking Portrait Synthesis via Audio-spatial Decomposition},
  author={Tang, Jiaxiang and Wang, Kaisiyuan and Zhou, Hang and Chen, Xiaokang and He, Dongliang and Hu, Tianshu and Liu, Jingtuo and Zeng, Gang and Wang, Jingdong},
  journal={arXiv preprint arXiv:2211.12368},
  year={2022}
}
```
