<h1 align="center">Metaball</h1>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white" /></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-≥2.5.0-ee4c2c?logo=pytorch&logoColor=white" /></a>
  <a href="https://www.3ds.com/products/simulia/abaqus/"><img src="https://img.shields.io/badge/Abaqus-≥2022-005386?logo=dassaultsystemes&logoColor=white" /></a>
  <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-4.10.0-5c3ee8?logo=opencv&logoColor=white" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-black?logo=open-source-initiative&logoColor=white" /></a>
  <br/>
  <a href="./docs/training.ipynb">⚡Training Guide</a> |
  <a href="./docs/assembly.md">🛠️Assembly Guide</a> |
  <a href="./docs/deployment.md">🤖Deployment Guide</a> |
  <a href="https://github.com/han-xudong/metaball-viewer">🫧Data Viewer</a> |
  <a href="https://a360.co/4ePH4PC">🧩CAD Files</a>
</p>
<p align="center">
  <img src="docs/assets/banner.jpg" alt="MagiClaw Banner" />
</p>

Metaball is a soft end-of-robot module capable of vision-based deformable perception. This repository contains the training and testing code for the BallNet model.

## 📦 Installation

Clone this repository and install the required packages:

```bash
git clone https://github.com/han-xudong/metaball.git
cd metaball
pip install torch torchvision torchaudio # CPU or CUDA version
pip install -e .
```

## ⚡ Training

Before training the model, you need to prepare the dataset according to the [training guide](./docs/training.ipynb). Then, run the following command to train the model:

```bash
python train.py --lr <lr> --batch_size <batch_size> --max_epochs <max_epochs>
```

where `<lr>`, `<batch_size>`, and `<max_epochs>` are the learning rate, batch size, and maximum number of epochs, respectively.

After training, it's recommended to export the model to ONNX format for deployment:

```bash
python scripts/export_onnx.py --ckpt_path <chpt_path>
```

where `<ckpt_path>` is the path to the trained model checkpoint. The exported ONNX model will be saved in the same directory as the checkpoint.

You can also follow the [training guide](./docs/training.ipynb) to test the model by calculating the R2 score, and RMSE, and visualizing the prediction results, etc.

## 🛠️ Hardware

The hardware of the Metaball module includes a camera, a microcontroller, a power board, and a soft body. The camera is used for capturing images, while the microcontroller publishes the images through TCP protocol. The power board supports 6-36V input and powers the microcontroller. The soft body is made of polyurethane (PU), which is the main part to interact with the environment.

CAD files of the Metaball are available on [Fusion](https://a360.co/4ePH4PC). You can also refer to the [assembly guide](./docs/assembly.md) for more details on how to assemble the Metaball.

## 🤖 Deployment

To deploy the Metaball, please follow the [deployment guide](./docs/deployment.md). After connecting the Metaball to the host computer or WiFi and modifying the configuration file, you can publish the data by running the following command:

```bash
python run_metaball.py
```

All data can be visualized through the [Metaball Viewer](https://github.com/han-xudong/metaball-viewer).

![Metaball Viewer](docs/assets/screenshot.jpg)

## 📄 License

This project is licensed under the [MIT License](LICENSE).
