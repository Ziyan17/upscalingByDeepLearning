The code models reactive transport in a multiscale fracture network using deep learning. To run the code:
1. Copy the files in "graphs" to openFoam postprocessing directory "~/OpenFoam/OpenFoam-v1712/etc/caseDicts/postProcessing/graphs"
2. Open the folder "project".
3. Run "mainProgram.py", which generates the training set.
4. Run "trainFluxInlet.py" to train a recurrent neural network that predicts mass flux at microcrack inlets.
5. Run "trainFluxOnlet.py" to train a recurrent neural network that predicts mass flux at microcrack outlets.
6. Run "simulation.py" to perform the multiscale modeling with neural networks.

Developed by Ziyan Wang.
