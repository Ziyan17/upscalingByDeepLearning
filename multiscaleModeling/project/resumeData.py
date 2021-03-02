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

from config import N, dt, tMax, porosity
import time


tArray = np.arange(dt, tMax + dt, dt, dtype=int)
sArray = tArray.astype(str)


def mainFractureRecordHelper():
    listData = []
    for s in sArray:
        os.chdir("./" + s)
        data = np.loadtxt("line_T_p.xy")
        listData.append(data)
        os.chdir("../")
    allData = np.stack(listData, axis=1)
    concentrationData = allData[:, :, 1]
    pressureData = allData[:, :, 2]
    return concentrationData, pressureData


def mainFractureRecord():
    os.chdir("./02mainFracture/postProcessing/netWallSamplingLeakyA")
    concentrationDataA, pressureDataA = mainFractureRecordHelper()
    os.chdir("../../../")
    os.chdir("./02mainFracture/postProcessing/netWallSamplingLeakyB")
    concentrationDataB, pressureDataB = mainFractureRecordHelper()
    os.chdir("../../../")
    os.chdir("./02mainFracture/postProcessing/netWallSamplingLeakyC")
    concentrationDataC, pressureDataC = mainFractureRecordHelper()
    os.chdir("../../../")
    os.chdir("./02mainFracture/postProcessing/netWallSamplingLeakyD")
    concentrationDataD, pressureDataD = mainFractureRecordHelper()
    os.chdir("../../../")

    concentrationDataInlet = np.concatenate((concentrationDataB, concentrationDataC), axis=0)
    concentrationDataOutlet = np.concatenate((concentrationDataA, concentrationDataD), axis=0)
    pressureDataInlet = np.concatenate((pressureDataB, pressureDataC), axis=0)
    pressureDataOutlet = np.concatenate((pressureDataA, pressureDataD), axis=0)
    np.savetxt('concentrationDataInlet.txt', concentrationDataInlet)
    np.savetxt('concentrationDataOutlet.txt', concentrationDataOutlet)
    np.savetxt('pressureDataInlet.txt', pressureDataInlet)
    np.savetxt('pressureDataOutlet.txt', pressureDataOutlet)
    return concentrationDataInlet, pressureDataInlet, concentrationDataOutlet, pressureDataOutlet


def microFractureRunHelper():
    listData = []
    for s in sArray:
        os.chdir("./" + s)
        data = np.loadtxt("line_U_f.xy")
        listData.append(data)
        os.chdir("../")
    allData = np.stack(listData, axis=1)
    meanData = np.mean(allData, axis=0) * porosity  ##### averaged for wall bc
    return meanData


def microFractureRun(concentrationDataInlet, pressureDataInlet, concentrationDataOutlet, pressureDataOutlet):

    os.chdir("./01microFracture")
    listResultsInlet = []
    listResultsOutlet = []

    for i in range(N):
        # Run simulation in a micro fracture with the i-th inlet data
        with open('TInlet.csv', 'w', newline='') as csvfile1:
            writer = csv.writer(csvfile1, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for t in tArray:
                writer.writerow([t, concentrationDataInlet[i, int(t / dt - 1)]])
        with open('pInlet.csv', 'w', newline='') as csvfile2:
            writer = csv.writer(csvfile2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for t in tArray:
                writer.writerow([t, pressureDataInlet[i, int(t/dt - 1)]])
        with open('TOutlet.csv', 'w', newline='') as csvfile3:
            writer = csv.writer(csvfile3, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for t in tArray:
                writer.writerow([t, concentrationDataOutlet[i, int(t / dt - 1)]])
        with open('pOutlet.csv', 'w', newline='') as csvfile4:
            writer = csv.writer(csvfile4, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for t in tArray:
                writer.writerow([t, pressureDataOutlet[i, int(t/dt - 1)]])

        # Run
        os.system('./gFoamEXE.out')
        # Record the inlet averaged mass flux and velocity
        os.chdir("./postProcessing/netMicroFractureInlet")
        meanDataInlet = microFractureRunHelper()
        listResultsInlet.append(meanDataInlet)
        os.chdir("../../")

        os.chdir("./postProcessing/netMicroFractureOutlet")
        meanDataOutlet = microFractureRunHelper()
        listResultsOutlet.append(meanDataOutlet)
        os.chdir("../../")

    resultsInlet = np.stack(listResultsInlet, axis=0)
    resultsOutlet = np.stack(listResultsOutlet, axis=0)
    os.chdir("../")
    velocityDataInlet = resultsInlet[:, :, 1]
    fluxDataInlet = resultsInlet[:, :, 4]
    velocityDataOutlet = - resultsOutlet[:, :, 1] # !!!!!! need negative sign for outlet
    fluxDataOutlet = - resultsOutlet[:, :, 4] # !!!!!! need negative sign for outlet
    np.savetxt('velocityDataInlet.txt', velocityDataInlet)
    np.savetxt('fluxDataInlet.txt', fluxDataInlet)
    np.savetxt('velocityDataOutlet.txt', velocityDataOutlet)
    np.savetxt('fluxDataOutlet.txt', fluxDataOutlet)
    return 0


def main():
    concentrationDataInlet, pressureDataInlet, concentrationDataOutlet, pressureDataOutlet = mainFractureRecord()
    microFractureRun(concentrationDataInlet, pressureDataInlet, concentrationDataOutlet, pressureDataOutlet)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))