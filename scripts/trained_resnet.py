from torchvision import transforms
import torch
from PIL import Image
from scripts.resnet_model import Net

# Define model: pre-trained_CNN


def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list, tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)


class DeviceDataLoader:
    """Wrap a dataloader to move data to a device"""

    def __init__(self, dl, device):
        self.dl = dl
        self.device = device

    def __iter__(self):
        """Yield a batch of data after moving it to device"""
        for b in self.dl:
            yield to_device(b, self.device)

    def __len__(self):
        """Number of batches"""
        return len(self.dl)


class MyModel:

    def __init__(self, trained_weights: str, device: str):
        self.net = Net()
        self.weights = trained_weights
        self.device = torch.device('cuda:0' if device == 'cuda' else 'cpu')
        self._initialize()

    def _initialize(self):
        # Load weights
        try:
            # Force loading on CPU if there is no GPU
            if torch.cuda.is_available() == False:
                self.net.load_state_dict(torch.load(self.weights,
                                                    map_location=lambda
                                                    storage, loc: storage)[
                                                    "state_dict"])
            else:
                self.net.load_state_dict(
                                        torch.load(self.weights)["state_dict"])

        except IOError:
            print("Error Loading Weights")
            return None
        self.net.eval()

        # Move to specified device
        self.net.to(self.device)

    def infer(self, path):
        img = Image.open(path)
        preprocess = transforms.Compose([
            transforms.Resize((300, 300)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]), ])
        image_tensor = preprocess(img)

        # create a mini-batch as expected by the model
        input_batch = to_device(image_tensor.unsqueeze(0), self.device)

        with torch.no_grad():
            output = self.net(input_batch)

        # The output has unnormalized scores. To get probabilities,  you can
        # run a softmax on it.
        confidence, index = torch.max(output, dim=1)
        return index[0].item(), confidence[0].item()
