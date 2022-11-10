#!/usr/bin/env python

from paraview.simple import *

# paraview 5.9 VS 5.10 compatibility ===========================================
def ThresholdBetween(threshold, lower, upper):
    try:
        # paraview 5.9
        threshold.ThresholdRange = [lower, upper]
    except:
        # paraview 5.10
        threshold.ThresholdMethod = "Between"
        threshold.LowerThreshold = lower
        threshold.UpperThreshold = upper


# end of comphatibility ========================================================

# create a new 'XML Unstructured Grid Reader'
tectonicPuzzlevtu = XMLUnstructuredGridReader(FileName=["tectonicPuzzle.vtu"])

# create a new 'Extract Surface'
extractSurface1 = ExtractSurface(Input=tectonicPuzzlevtu)

# create a new 'Clean to Grid'
cleantoGrid1 = CleantoGrid(Input=extractSurface1)

# create a new 'Tetrahedralize'
tetrahedralize1 = Tetrahedralize(Input=cleantoGrid1)

# create a new 'Connectivity'
connectivity1 = Connectivity(Input=tetrahedralize1)

# create a new 'Threshold'
threshold1 = Threshold(Input=connectivity1)
threshold1.Scalars = ["POINTS", "RegionId"]
ThresholdBetween(threshold1, 1.0, 1.0)

# create a new 'Calculator'
calculator1 = Calculator(Input=threshold1)
calculator1.ResultArrayName = "logViscosity"
calculator1.Function = "log10(Viscosity)"

# create a new 'TTK PersistenceDiagram'
tTKPersistenceDiagram1 = TTKPersistenceDiagram(Input=calculator1)
tTKPersistenceDiagram1.ScalarField = ["POINTS", "logViscosity"]

# create a new 'Threshold'
threshold2 = Threshold(Input=tTKPersistenceDiagram1)
threshold2.Scalars = ["CELLS", "PairIdentifier"]
ThresholdBetween(threshold2, -0.1, 999999999)

# create a new 'Threshold'
persistenceThreshold = Threshold(Input=threshold2)
persistenceThreshold.Scalars = ["CELLS", "Persistence"]
ThresholdBetween(persistenceThreshold, 0.5, 999999999)

# create a new 'TTK IcospheresFromPoints'
tTKIcospheresFromPoints1 = TTKIcospheresFromPoints(Input=persistenceThreshold)
tTKIcospheresFromPoints1.Radius = 0.5

# create a new 'TTK TopologicalSimplification'
tTKTopologicalSimplification1 = TTKTopologicalSimplification(
    Domain=calculator1, Constraints=persistenceThreshold
)
tTKTopologicalSimplification1.ScalarField = ["POINTS", "logViscosity"]

# create a new 'TTK MorseSmaleComplex'
tTKMorseSmaleComplex1 = TTKMorseSmaleComplex(Input=tTKTopologicalSimplification1)
tTKMorseSmaleComplex1.ScalarField = ["POINTS", "logViscosity"]

# create a new 'TTK IcospheresFromPoints'
tTKIcospheresFromPoints2 = TTKIcospheresFromPoints(Input=tTKMorseSmaleComplex1)
tTKIcospheresFromPoints2.Radius = 0.1

# create a new 'Threshold'
threshold3 = Threshold(Input=tTKIcospheresFromPoints2)
threshold3.Scalars = ["POINTS", "CellDimension"]
ThresholdBetween(threshold3, 2.0, 2.0)

# create a new 'Threshold'
lARGE_MAXIMA_THRESHOLD = Threshold(Input=threshold3)
lARGE_MAXIMA_THRESHOLD.Scalars = ["POINTS", "ManifoldSize"]
ThresholdBetween(lARGE_MAXIMA_THRESHOLD, 75.0, 999999999)

# create a new 'Threshold'
pERSISTENT_MINIMA = Threshold(Input=tTKIcospheresFromPoints1)
pERSISTENT_MINIMA.Scalars = ["POINTS", "CriticalType"]

# create a new 'Append Datasets'
pERSISTENT_MINIMA_AND_LARGE_MAXIMA = AppendDatasets(
    Input=[pERSISTENT_MINIMA, lARGE_MAXIMA_THRESHOLD]
)

# create a new 'TTK TopologicalSimplification'
tTKTopologicalSimplification2 = TTKTopologicalSimplification(
    Domain=tTKTopologicalSimplification1, Constraints=pERSISTENT_MINIMA_AND_LARGE_MAXIMA
)
tTKTopologicalSimplification2.ScalarField = ["POINTS", "logViscosity"]

# create a new 'TTK PersistenceDiagram'
tTKPersistenceDiagram2 = TTKPersistenceDiagram(Input=tTKTopologicalSimplification2)
tTKPersistenceDiagram2.ScalarField = ["POINTS", "logViscosity"]

# create a new 'Threshold'
threshold4 = Threshold(Input=tTKPersistenceDiagram2)
threshold4.Scalars = ["CELLS", "PairIdentifier"]
ThresholdBetween(threshold4, -0.1, 999999999)

# create a new 'Threshold'
threshold5 = Threshold(Input=threshold4)
threshold5.Scalars = ["CELLS", "PairType"]
ThresholdBetween(threshold5, 1.0, 1.0)

# create a new 'Calculator'
calculator2 = Calculator(Input=threshold5)
calculator2.ResultArrayName = "SaddleValue"
calculator2.Function = "coordsX"

# create a new 'Threshold'
sADDLE_VALUE_THRESHOLD = Threshold(Input=calculator2)
sADDLE_VALUE_THRESHOLD.Scalars = ["POINTS", "SaddleValue"]
ThresholdBetween(sADDLE_VALUE_THRESHOLD, -0.2, 1.75)

# create a new 'TTK IcospheresFromPoints'
tTKIcospheresFromPoints3 = TTKIcospheresFromPoints(Input=sADDLE_VALUE_THRESHOLD)
tTKIcospheresFromPoints3.Radius = 0.5

# create a new 'Threshold'
lARGE_MAXIMA_LOW_SADDLE = Threshold(Input=tTKIcospheresFromPoints3)
lARGE_MAXIMA_LOW_SADDLE.Scalars = ["POINTS", "CriticalType"]
ThresholdBetween(lARGE_MAXIMA_LOW_SADDLE, 3.0, 3.0)

# create a new 'Append Datasets'
lARGE_MAXIMA_LOW_SADDLE_AND_PERSISTENT_MINIMA = AppendDatasets(
    Input=[pERSISTENT_MINIMA, lARGE_MAXIMA_LOW_SADDLE]
)

# create a new 'TTK TopologicalSimplification'
tTKTopologicalSimplification3 = TTKTopologicalSimplification(
    Domain=tTKTopologicalSimplification2,
    Constraints=lARGE_MAXIMA_LOW_SADDLE_AND_PERSISTENT_MINIMA,
)
tTKTopologicalSimplification3.ScalarField = ["POINTS", "logViscosity"]

# create a new 'TTK MorseSmaleComplex'
tTKMorseSmaleComplex2 = TTKMorseSmaleComplex(Input=tTKTopologicalSimplification3)
tTKMorseSmaleComplex2.ScalarField = ["POINTS", "logViscosity"]

# create a new 'TTK IdentifierRandomizer'
tTKIdentifierRandomizer1 = TTKIdentifierRandomizer(
    Input=OutputPort(tTKMorseSmaleComplex2, 3)
)
tTKIdentifierRandomizer1.ScalarField = ["POINTS", "AscendingManifold"]

SaveData("Segmentation.vtu", tTKIdentifierRandomizer1)
