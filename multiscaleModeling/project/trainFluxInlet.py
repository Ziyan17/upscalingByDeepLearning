from __future__ import print_function
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

class Sequence(nn.Module):
    def __init__(self):
        super(Sequence, self).__init__()
        self.lstm1 = nn.LSTMCell(2, 51)
        self.lstm2 = nn.LSTMCell(51, 51)
        self.linear = nn.Linear(51, 1)

    def forward(self, input, future = 0):
        outputs = []
        h_t = torch.zeros(input.size(1), 51, dtype=torch.double)
        c_t = torch.zeros(input.size(1), 51, dtype=torch.double)
        h_t2 = torch.zeros(input.size(1), 51, dtype=torch.double)
        c_t2 = torch.zeros(input.size(1), 51, dtype=torch.double)

        for i in range(input.size(0)):
            input_t = input[i]
         #   , input_t in enumerate(input.chunk(input.size(1), dim=1))
            h_t, c_t = self.lstm1(input_t, (h_t, c_t))
            h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2))
            output = self.linear(h_t2)
            outputs += [output]
        for i in range(future):# if we should predict the future
            h_t, c_t = self.lstm1(output, (h_t, c_t))
            h_t2, c_t2 = self.lstm2(h_t, (h_t2, c_t2))
            output = self.linear(h_t2)
            outputs += [output]
        outputs = torch.stack(outputs, 1).squeeze(2)
        return outputs


if __name__ == '__main__':
    # set random seed to 0
    start_time = time.time()
    np.random.seed(0)
    torch.manual_seed(0)
    # load data and make training set
    data_T_inlet = np.loadtxt('concentrationDataInlet.txt')
    data_T_inlet = np.transpose(data_T_inlet)
    data_T_outlet = np.loadtxt('concentrationDataOutlet.txt')
    data_T_outlet = np.transpose(data_T_outlet)
    ## data_p = np.loadtxt('pressureData.txt')
    ## data_p = np.transpose(data_p)
    ## data_p = data_p * 1e8 # rescale data

    data = np.stack((data_T_inlet, data_T_outlet), axis=-1)
    data2 = np.loadtxt('fluxDataInlet.txt')
    data2 = data2 /100 # *1e10 # /100   # rescale data

   # input = torch.from_numpy(np.delete(data[0:50], [8, 9, 10], 0))
   # target = torch.from_numpy(np.delete(data2[0:50], [8, 9, 10], 0))
    input = torch.from_numpy(data)
    target = torch.from_numpy(data2)
    test_input = torch.from_numpy(data[:, 1:4, :])
    test_target = torch.from_numpy(data2[1:4, :])
    '''
    data = torch.load('traindata.pt')
    data2 = torch.load('traindata2.pt')
    input = torch.from_numpy(data[3:, :])
    target = torch.from_numpy(data2[3:, :])
    test_input = torch.from_numpy(data[:3, :])
    test_target = torch.from_numpy(data2[:3, :])
    '''
    # build the model
    seq = Sequence()
    seq.double()
    criterion = nn.MSELoss()
    # use LBFGS as optimizer since we can load the whole data to train
    optimizer = optim.LBFGS(seq.parameters(), lr=0.2)
    #begin to train
    for i in range(30):
        print('STEP: ', i)
        def closure():
            optimizer.zero_grad()
            out = seq(input)
            loss = criterion(out, target)
            print('loss:', loss.item())
            loss.backward()
            return loss
        optimizer.step(closure)
        torch.save(seq.state_dict(), 'neuralFluxInlet.pt')

        model = Sequence()
        model.double()
        model.load_state_dict(torch.load('neuralFluxInlet.pt'))
        model.eval()
        # begin to predict, no need to track gradient here
        with torch.no_grad():
            future = 0
            pred = model(test_input, future=future)
            loss = criterion(pred, test_target)
            print('test loss:', loss.item())
            y = pred.detach().numpy()

        # draw the result
        plt.figure(figsize=(30,10))
      #  plt.title('Predict future values for time sequences\n(Dashlines are predicted values)', fontsize=30)
        plt.xlabel('x', fontsize=20)
        plt.ylabel('y', fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        def draw(yi, color):
            plt.plot(np.arange(test_input.size(0)), yi[:test_input.size(0)], color, linewidth = 2.0)
     #       plt.plot(np.arange(input.size(1), input.size(1) + future), yi[input.size(1):], color + ':', linewidth = 2.0)
        draw(y[0], 'r')
        draw(y[1], 'g')
        draw(y[2], 'b')
        draw(test_target[0].numpy(), 'y')
        draw(test_target[1].numpy(), 'm')
        draw(test_target[2].numpy(), 'k')
        plt.savefig('predict%d.pdf'%i)
        plt.close()
    print("--- %s seconds ---" % (time.time() - start_time))
