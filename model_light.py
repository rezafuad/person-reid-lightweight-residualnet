import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init, Parameter
from torchvision import models
from torch.autograd import Variable
import pretrainedmodels
import net_sphere 
import base_cl as bcl
from pyramidpooling import *

import pyramidpooling as pyrpool
import resnet

######################################################################
def weights_init_kaiming(m):
    classname = m.__class__.__name__
    # print(classname)
    if classname.find('Conv') != -1:
        init.kaiming_normal_(m.weight.data, a=0, mode='fan_in') # For old pytorch, you may use kaiming_normal.
    elif classname.find('Linear') != -1:
        init.kaiming_normal_(m.weight.data, a=0, mode='fan_out')
        init.constant_(m.bias.data, 0.0)
    elif classname.find('BatchNorm1d') != -1:
        init.normal_(m.weight.data, 1.0, 0.02)
        init.constant_(m.bias.data, 0.0)

def weights_init_classifier(m):
    classname = m.__class__.__name__
    if classname.find('Linear') != -1:
        init.normal_(m.weight.data, std=0.001)
        init.constant_(m.bias.data, 0.0)

# Defines the new fc layer and classification layer
# |--Linear--|--bn--|--relu--|--Linear--|
class ClassBlock(nn.Module):
    def __init__(self, input_dim, class_num, droprate, relu=False, bnorm=True, num_bottleneck=512, linear=True, return_f = False):
        super(ClassBlock, self).__init__()
        self.return_f = return_f
        add_block = []
        if linear:
            add_block += [nn.Linear(input_dim, num_bottleneck)]
        else:
            num_bottleneck = input_dim
        if bnorm:
            add_block += [nn.BatchNorm1d(num_bottleneck)]
        if relu:
            add_block += [nn.LeakyReLU(0.1)]
        if droprate>0:
            add_block += [nn.Dropout(p=droprate)]
        add_block = nn.Sequential(*add_block)
        add_block.apply(weights_init_kaiming)

        classifier = []
        classifier += [nn.Linear(num_bottleneck, class_num)]
        classifier = nn.Sequential(*classifier)
        classifier.apply(weights_init_classifier)

        self.add_block = add_block
        self.classifier = classifier
    def forward(self, x):
        x = self.add_block(x)
        if self.return_f:
            f = x
            x = self.classifier(x)
            return x,f
        else:
            x = self.classifier(x)
            return x


# Defines the new fc layer and classification layer
# |--Linear--|--bn--|--relu--|--Linear--|
class ClassBlockV2(nn.Module):
    def __init__(self, input_dim, class_num, droprate, relu=False, bnorm=True, num_bottleneck=512, linear=True, return_f = False):
        super(ClassBlockV2, self).__init__()
        self.return_f = return_f
        add_block = []
        if linear:
            add_block += [nn.Linear(input_dim, num_bottleneck)]
            add_block += [nn.BatchNorm1d(num_bottleneck)]
            add_block += [nn.LeakyReLU(0.1)]
            add_block += [nn.Linear(num_bottleneck, num_bottleneck)]
        else:
            num_bottleneck = input_dim
        if bnorm:
            add_block += [nn.BatchNorm1d(num_bottleneck)]
        if relu:
            add_block += [nn.LeakyReLU(0.1)]
        if droprate>0:
            add_block += [nn.Dropout(p=droprate)]
        add_block = nn.Sequential(*add_block)
        add_block.apply(weights_init_kaiming)

        classifier = []
        classifier += [nn.Linear(num_bottleneck, class_num)]
        classifier = nn.Sequential(*classifier)
        classifier.apply(weights_init_classifier)

        self.add_block = add_block
        self.classifier = classifier
    def forward(self, x):
        x = self.add_block(x)
        if self.return_f:
            f = x
            x = self.classifier(x)
            return x,f
        else:
            x = self.classifier(x)
            return x


###################################################################################################

# Define the ResNet20-based Model
class ft_net20(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net20, self).__init__()
        self.add_module("module", resnet.resnet20())
        weights_ = torch.load("weights_cifar10/resnet20-12fca82f.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

###################################################################################################

# Define the ResNet32-based Model
class ft_net32(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net32, self).__init__()
        self.add_module("module", resnet.resnet32())
        weights_ = torch.load("weights_cifar10/resnet32-d509ac18.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

###################################################################################################


# Define the ResNet44-based Model
class ft_net44(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net44, self).__init__()
        self.add_module("module", resnet.resnet44())
        weights_ = torch.load("weights_cifar10/resnet44-014dd654.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

###################################################################################################


# Define the ResNet56-based Model
class ft_net56(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net56, self).__init__()
        self.add_module("module", resnet.resnet56())
        weights_ = torch.load("weights_cifar10/resnet56-4bfd9763.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

###################################################################################################


# Define the ResNet110-based Model
class ft_net110(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net110, self).__init__()
        self.add_module("module", resnet.resnet110())
        weights_ = torch.load("weights_cifar10/resnet110-1d1ed7c2.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

# Define the ResNet110-based Model
class ft_net110_fc1024(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net110_fc1024, self).__init__()
        self.add_module("module", resnet.resnet110())
        weights_ = torch.load("weights_cifar10/resnet110-1d1ed7c2.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=1024)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

# Define the ResNet110-based Model
class ft_net110_fc768(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net110_fc768, self).__init__()
        self.add_module("module", resnet.resnet110())
        weights_ = torch.load("weights_cifar10/resnet110-1d1ed7c2.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=768)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

# Define the ResNet110-based Model
class ft_net110_fc256(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net110_fc256, self).__init__()
        self.add_module("module", resnet.resnet110())
        weights_ = torch.load("weights_cifar10/resnet110-1d1ed7c2.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=256)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

# Define the ResNet110-based Model
class ft_net110_fc128(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net110_fc128, self).__init__()
        self.add_module("module", resnet.resnet110())
        weights_ = torch.load("weights_cifar10/resnet110-1d1ed7c2.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=128)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x


###################################################################################################



class ft_net56_fc1024(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net56_fc1024, self).__init__()
        self.add_module("module", resnet.resnet56())
        weights_ = torch.load("weights_cifar10/resnet56-4bfd9763.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=1024)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

class ft_net56_fc768(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net56_fc768, self).__init__()
        self.add_module("module", resnet.resnet56())
        weights_ = torch.load("weights_cifar10/resnet56-4bfd9763.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=768)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

class ft_net56_fc256(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net56_fc256, self).__init__()
        self.add_module("module", resnet.resnet56())
        weights_ = torch.load("weights_cifar10/resnet56-4bfd9763.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=256)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x

class ft_net56_fc128(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net56_fc128, self).__init__()
        self.add_module("module", resnet.resnet56())
        weights_ = torch.load("weights_cifar10/resnet56-4bfd9763.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        self.classifier = ClassBlock(64, class_num, droprate, num_bottleneck=128)

    def forward(self, x):
        x = self.module(x)
        
        x = self.classifier(x)
        return x


###################################################################################################


# Define the ResNet110-based Model + SPP
class ft_net110_spp(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net110_spp, self).__init__()
        self.add_module("module", resnet.resnet110())
        weights_ = torch.load("weights_cifar10/resnet110-1d1ed7c2.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        ####
        self.spp = pyrpool.SpatialPyramidPooling((1,2))
        self.classifier = ClassBlock(320, class_num, droprate, num_bottleneck=128)

    def forward(self, x):
        #x = self.module(x)

        x = F.relu(self.module.bn1(self.module.conv1(x)))
        x = self.module.layer1(x)
        x = self.module.layer2(x)
        x = self.module.layer3(x)

        x = self.spp(x)

        x = self.classifier(x)
        return x


# Define the ResNet56-based Model + SPP
class ft_net56_spp(nn.Module):

    def __init__(self, class_num, droprate=0.5, stride=2):
        super(ft_net56_spp, self).__init__()
        self.add_module("module", resnet.resnet56())
        weights_ = torch.load("weights_cifar10/resnet56-4bfd9763.th")
        self.load_state_dict(weights_['state_dict'])
        self.module.linear = nn.Sequential()
        ####
        self.spp = pyrpool.SpatialPyramidPooling((1,2))
        self.classifier = ClassBlock(320, class_num, droprate, num_bottleneck=128)

    def forward(self, x):
        #x = self.module(x)

        x = F.relu(self.module.bn1(self.module.conv1(x)))
        x = self.module.layer1(x)
        x = self.module.layer2(x)
        x = self.module.layer3(x)

        x = self.spp(x)

        x = self.classifier(x)
        return x





###################################################################################################



'''
# debug model structure
# Run this code with:
python model.py
'''
if __name__ == '__main__':
# Here I left a simple forward function.
# Test the model, before you train it. 
    net = ft_net(751, stride=1)
    net.classifier = nn.Sequential()
    print(net)
    input = Variable(torch.FloatTensor(8, 3, 256, 128))
    output = net(input)
    print('net output size:')
    print(output.shape)
