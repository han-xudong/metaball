# Metaball

[![Python](https://img.shields.io/badge/python-≥3.10-3776AB?style=flat-square&logo=python)](https://www.python.org) [![PyTorch](https://img.shields.io/badge/pytorch-≥2.5.0-ee4c2c?style=flat-square&logo=pytorch)](https://pytorch.org) [![Abaqus](https://img.shields.io/badge/abaqus-≥2022-005386?style=flat-square&logo=dassaultsystemes)](https://www.3ds.com/products/simulia/abaqus) [![OpenCV](https://img.shields.io/badge/opencv-≥4.5.3-5c3ee8?style=flat-square&logo=opencv)](https://opencv.org) [![License](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)

[[Documentation]](https://metaball.github.io) | [[Guide]](./docs/guide.ipynb) | [[Viewer]](https://github.com/han-xudong/metaball-viewer) | [[CAD Files]](https://cad.onshape.com/documents/0c01c26edd5ce7dd82492ac0/v/5c49b5c2d03945d2841ede8e/e/d55ed0ae6b54a725fa4a191a?renderMode=0&uiState=6768cbc421f80738c6221e09)

Metaball is a soft end-of-robot module capable of vision-based deformable perception. This repository contains the training and testing code for the BallNet model.

## Installation

Clone this repository and install the required packages:

```bash
git clone https://github.com/han-xudong/metaball.git
cd metaball
pip install torch torchvision torchaudio # CPU or CUDA version
pip install -r requirements.txt
```

## Quick Start

Before training the model, you need to prepare the dataset according to the [guide](./docs/guide.ipynb). Then, run the following command to train the model:

```bash
python train.py
```

After training, follow the [guide](./docs/guide.ipynb) to test the model by calculating the R2 score, and RMSE, and visualizing the prediction results, etc.

## Hardware

The hardware of the Metaball module includes a camera, a microcontroller, and a soft body. The camera is used for capturing images, while the microcontroller publishes the images through TCP protocol. The soft body is made of polyurethane (PU), which is the main part to interact with the environment.

CAD files of the Metaball module are available in the [Onshape](https://cad.onshape.com/documents/0c01c26edd5ce7dd82492ac0/v/5c49b5c2d03945d2841ede8e/e/d55ed0ae6b54a725fa4a191a?renderMode=0&uiState=6768cbc421f80738c6221e09).

## Deployment

To deploy the Metaball, please follow the [deployment guide](./docs/deployment.md). After connecting the Metaball to the host computer or WiFi and modifying the configuration file, you can publish the data by running the following command:

```bash
python run_metaball.py
```

All data can be visualized through the [Metaball Viewer](https://github.com/han-xudong/metaball-viewer).

## License

This project is licensed under the [MIT License](LICENSE).
