from __future__ import print_function
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import csv
import time
from config import N, dt, tMax, porosity, maxIteration, errorMachine, nGrid, tCurrent


concentrationInitial = np.zeros(nGrid)
pressureInitial = np.zeros(nGrid)
tArray = np.arange(dt, tMax + dt, dt, dtype=int)
sArray = tArray.astype(str)

isExplict = 0
if isExplict == 1:
    maxIteration = 1


class Sequence(nn.Module):
    def __init__(self):
        super(Sequence, self).__init__()
        self.lstm1 = nn.LSTMCell(2, 51)
        self.lstm2 = nn.LSTMCell(51, 51)
        self.linear = nn.Linear(51, 1)

    def forward(self, input, h_t, c_t, h_t2, c_t2, future = 0):
        outputs = []
        if input.size(0) > 0:
            lastIndex = input.size(0) - 1
            input_t = input[lastIndex]
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
        return outputs, h_t, c_t, h_t2, c_t2


def loadNeuralNetwork():
    modelFluxInlet = Sequence()
    modelFluxInlet.double()
    modelFluxInlet.load_state_dict(torch.load('neuralFluxInlet.pt'))
    modelFluxInlet.eval()

    modelFluxOutlet = Sequence()
    modelFluxOutlet.double()
    modelFluxOutlet.load_state_dict(torch.load('neuralFluxOutlet.pt'))
    modelFluxOutlet.eval()

    return modelFluxInlet, modelFluxOutlet


def mainFractureRun():
    os.chdir("./02mainFracture")
    os.system('./gFoamEXE.out')
    os.chdir("../")


def mainFractureRecord(t):

    os.chdir("./02mainFracture")
    s = str(t)
    os.chdir("./" + s)
    newData = np.genfromtxt("T", skip_header=23, max_rows=15000)
    newDataA = newData[4500:5000]
    newDataB = newData[5000:5500]
    newDataC = newData[9500:10000]
    newDataD = newData[10000:10500]
    os.chdir("../")
    os.chdir("../")
    return newDataA, newDataB, newDataC, newDataD


def predictInlet(concentrationDataInlet, concentrationDataOutlet, modelFluxInlet, state):
    # load data
    data_T_inlet = concentrationDataInlet
    data_T_inlet = np.transpose(data_T_inlet)
    data_T_outlet = concentrationDataOutlet
    data_T_outlet = np.transpose(data_T_outlet)

    data = np.stack((data_T_inlet, data_T_outlet), axis=-1)

    input = torch.from_numpy(data)

    # predict mass flux at inlet
    modelFluxInlet.eval()
    # begin to predict, no need to track gradient here
    with torch.no_grad():
        h_t = state[0]
        c_t = state[1]
        h_t2 = state[2]
        c_t2 = state[3]

        future = 0
        pred, h_t, c_t, h_t2, c_t2 = modelFluxInlet(input, h_t, c_t, h_t2, c_t2, future=future)
        newState = [h_t, c_t, h_t2, c_t2]
        y = pred.detach().numpy()
    # re-scale y (make it dimensional again)
    # np.savetxt('massFlux.txt', y[:, -1] * 100)  # /1e10  # *100.0
    massFluxInlet = y[:, -1] * 100 # /1e10  # *100.0

    return massFluxInlet, newState


def predictOutlet(concentrationDataInlet, concentrationDataOutlet, modelFluxOutlet, state):
    # load data
    data_T_inlet = concentrationDataInlet
    data_T_inlet = np.transpose(data_T_inlet)
    data_T_outlet = concentrationDataOutlet
    data_T_outlet = np.transpose(data_T_outlet)

    data = np.stack((data_T_inlet, data_T_outlet), axis=-1)

    input = torch.from_numpy(data)

    # predict mass flux at outlet
    modelFluxOutlet.eval()
    # begin to predict, no need to track gradient here
    with torch.no_grad():
        future = 0
        h_t = state[0]
        c_t = state[1]
        h_t2 = state[2]
        c_t2 = state[3]
        pred, h_t, c_t, h_t2, c_t2 = modelFluxOutlet(input, h_t, c_t, h_t2, c_t2, future=future)
        newState = [h_t, c_t, h_t2, c_t2]
        y = pred.detach().numpy()
    # re-scale y (make it dimensional again)
    # np.savetxt('massFlux.txt', y[:, -1] * 100)  # /1e10  # *100.0
    massFluxOutlet = y[:, -1] * 100 # /1e10  # *100.0

    return massFluxOutlet, newState

def updateWallBOundary(massFlux, filename):
    if isExplict == 1:
        # !!!!!!!!!!!!!!!!!!!!!!!!
        return 0
    if isExplict == 0:
        os.chdir("./02mainFracture")
        previousMassFlux = np.loadtxt(filename) #'gradT.txt'
        relaxedMassFlux = (massFlux + previousMassFlux) / 2.0
        np.savetxt(filename, relaxedMassFlux)
        os.chdir("../")

        errorMassFlux = np.abs(massFlux - previousMassFlux)
        errorMaxMassFlux = np.amax(errorMassFlux)

        return errorMaxMassFlux


def deleteResults(t):
    os.system('rm -rf ./02mainFracture/' + str(t))


def main():
    concentrationListA = []
    concentrationListB = []
    concentrationListC = []
    concentrationListD = []
    concentrationListA.append(concentrationInitial)
    concentrationListB.append(concentrationInitial)
    concentrationListC.append(concentrationInitial)
    concentrationListD.append(concentrationInitial)
    modelFluxInlet, modelFluxOutlet = loadNeuralNetwork()


    h_t = torch.zeros(nGrid, 51, dtype=torch.double)  # input.size(1) = nGrid
    c_t = torch.zeros(nGrid, 51, dtype=torch.double)
    h_t2 = torch.zeros(nGrid, 51, dtype=torch.double)
    c_t2 = torch.zeros(nGrid, 51, dtype=torch.double)

    stateA = [h_t, c_t, h_t2, c_t2]
    stateB = stateA.copy()
    stateC = stateA.copy()
    stateD = stateA.copy()

    for t in tArray:
        if t <= tCurrent:
            newDataA, newDataB, newDataC, newDataD = mainFractureRecord(t)
            newConcentrationDataA = newDataA
            newConcentrationDataB = newDataB
            newConcentrationDataC = newDataC
            newConcentrationDataD = newDataD

            concentrationListA.append(newConcentrationDataA)
            concentrationListB.append(newConcentrationDataB)
            concentrationListC.append(newConcentrationDataC)
            concentrationListD.append(newConcentrationDataD)

        else:     		
            for iteration in range(maxIteration):
                mainFractureRun()
                newDataA, newDataB, newDataC, newDataD = mainFractureRecord(t)
                newConcentrationDataA = newDataA
                newConcentrationDataB = newDataB
                newConcentrationDataC = newDataC
                newConcentrationDataD = newDataD

                tempConcentrationListA = concentrationListA.copy()
                tempConcentrationListB = concentrationListB.copy()
                tempConcentrationListC = concentrationListC.copy()
                tempConcentrationListD = concentrationListD.copy()

                tempConcentrationListA.append(newConcentrationDataA)
                tempConcentrationListB.append(newConcentrationDataB)
                tempConcentrationListC.append(newConcentrationDataC)
                tempConcentrationListD.append(newConcentrationDataD)

                tempConcentrationDataA = np.stack(tempConcentrationListA, axis=1)
                tempConcentrationDataB = np.stack(tempConcentrationListB, axis=1)
                tempConcentrationDataC = np.stack(tempConcentrationListC, axis=1)
                tempConcentrationDataD = np.stack(tempConcentrationListD, axis=1)

                massFluxB, tempStateB = predictInlet(tempConcentrationDataB, tempConcentrationDataA, modelFluxInlet, stateB)
                massFluxA, tempStateA = predictOutlet(tempConcentrationDataB, tempConcentrationDataA, modelFluxOutlet, stateA)
                massFluxC, tempStateC = predictInlet(tempConcentrationDataC, tempConcentrationDataD, modelFluxInlet, stateC)
                massFluxD, tempStateD = predictOutlet(tempConcentrationDataC, tempConcentrationDataD, modelFluxOutlet, stateD)

                errorMaxMassFluxA = updateWallBOundary(massFluxA, 'gradTA.txt')
                errorMaxMassFluxB = updateWallBOundary(massFluxB, 'gradTB.txt')
                errorMaxMassFluxC = updateWallBOundary(massFluxC, 'gradTC.txt')
                errorMaxMassFluxD = updateWallBOundary(massFluxD, 'gradTD.txt')

                if errorMaxMassFluxB < 0.01 * np.amax(np.abs(massFluxB)):
                    concentrationListA = tempConcentrationListA.copy()
                    concentrationListB = tempConcentrationListB.copy()
                    concentrationListC = tempConcentrationListC.copy()
                    concentrationListD = tempConcentrationListD.copy()
                    stateA = tempStateA.copy()
                    stateB = tempStateB.copy()
                    stateC = tempStateC.copy()
                    stateD = tempStateD.copy()
                    break

                if iteration == maxIteration - 1:
                    concentrationListA = tempConcentrationListA.copy()
                    concentrationListB = tempConcentrationListB.copy()
                    concentrationListC = tempConcentrationListC.copy()
                    concentrationListD = tempConcentrationListD.copy()
                    stateA = tempStateA.copy()
                    stateB = tempStateB.copy()
                    stateC = tempStateC.copy()
                    stateD = tempStateD.copy()
                    break

                deleteResults(t)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
