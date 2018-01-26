import torch
import torch.nn as nn


class Net(torch.nn.Module):
    def __init__(self, num_channels, scale_factor, d=56, s=12, m=4):
        super(Net, self).__init__()

        # Feature extraction
        self.first_part = nn.Sequential(nn.Conv2d(in_channels=num_channels, out_channels=d, kernel_size=5, stride=1, padding=0),
                                        nn.PReLU())

        self.layers = []
        # Shrinking
        self.layers.append(nn.Sequential(nn.Conv2d(in_channels=d, out_channels=s, kernel_size=1, stride=1, padding=0),
                                         nn.PReLU()))
        # Non-linear Mapping
        for _ in range(m):
            self.layers.append(nn.Conv2d(in_channels=s, out_channels=s, kernel_size=3, stride=1, padding=0))
        self.layers.append(nn.PReLU())
        # Expanding
        self.layers.append(nn.Sequential(nn.Conv2d(in_channels=s, out_channels=d, kernel_size=1, stride=1, padding=0),
                                         nn.PReLU()))

        self.mid_part = torch.nn.Sequential(*self.layers)

        # Deconvolution
        self.last_part = nn.ConvTranspose2d(in_channels=d, out_channels=num_channels, kernel_size=9, stride=scale_factor, padding=3, output_padding=1)

    def forward(self, x):
        out = self.first_part(x)
        out = self.mid_part(out)
        out = self.last_part(out)
        return out

    def weight_init(self, mean=0.0, std=0.02):
        for m in self.modules():
            # utils.weights_init_normal(m, mean=mean, std=std)
            if isinstance(m, nn.Conv2d):
                m.weight.data.normal_(mean, std)
                if m.bias is not None:
                    m.bias.data.zero_()
            if isinstance(m, nn.ConvTranspose2d):
                m.weight.data.normal_(0.0, 0.0001)
                if m.bias is not None:
                    m.bias.data.zero_()