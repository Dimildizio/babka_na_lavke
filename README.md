# Babka na lavke - Telegram face detector, age and misgender classification

![babuskas](https://github.com/Dimildizio/babka_na_lavke/assets/42382713/fe8663d1-ef9c-43d9-9508-bdb0e1c49488)


In our modern world where technology advances at an incredible pace, we often lose touch with the simple yet soulful things from the past. Who doesn't recall the scene from their childhood: the old Khrushchyovka buildings, the cozy courtyards, and, of course, the grandmother on the bench, watching over everyone and calling things the way they actually are. Times change, no more grandmas sitting next to the soulless apartment buildings, however thanks to the latest developments in artificial intelligence, we've found a way to recreate that atmosphere.

Babka na lavke is a Telegram bot that allows users to detect faces and misgender them in images.



## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    
- [Usage](#usage)
  - [Commands](#commands)
  - [Face Classification](#face-classification)
  - [Examples](#examples)
  - 
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

To run Babka locally or on your own server, you will need the following:

- Python 3.10+
- Microsoft Visual C++ 14 Build tools 
- Telegram bot token
- ONNX model file (train your own or follow [this](https://github.com/deepinsight/insightface/tree/master/examples/in_swapper) insightface guidline to get)
- 

### Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Dimildizio/babka_na_lavke.git

2. Install dependencies:

Use poetry for that.

3. Set up your bot token:
  Create a bot on Telegram and obtain your API token.


4. Create a **config.yaml** file in the project directory and add your token and other necessary data.
  You can find an example of **config.yaml** [here](https://github.com/Dimildizio/babka_na_lavke/blob/main/src/config_example.yaml)

5. Go to the /predictor folder, put your onnx file there (default is inswapper_128.oonx) and run Fast API
   ```shell
   cd src/predictor
   uvicorn model:app --reload


8. Run main.py to start the bot

## Usage

### **Commands**

Babka supports several commands that users can send in their Telegram chats to interact with the bot. Here are some common commands:

- `/start`: Start the bot.

One is supposed to send images with faces on it to Babka. Babka is deaf so she won't listen to anything you say and of course she is already too blind to read.

### **Face Classification**

To classify faces in an image, simply send a photo to the bot. If the image contains faces, the bot will process it and return the image with (a) class(es) on it. 


### **Examples**

Here are some examples of face detection and misgendering:

![babka_classificator](https://github.com/Dimildizio/babka_na_lavke/assets/42382713/5fada100-20f3-4f41-bd17-c2f66f4a0b16)


## **Contributing**

Contributions to Babka are not welcome! It is a humorous project that is not going to be supported, however if you have ideas for improvements, bug reports, or feature requests, please open an issue.

## **License**

This project is licensed under the MIT License.
