#Author-Scott Kildall
#Description-Finger Joint Box for Fusion 360

import adsk.core, adsk.fusion

# width = x
# depth = z
# height = z
def buildBox(rootComp,w,h,d,th): 
    sketch = addXYPlane(rootComp)
    buildSide(rootComp,sketch,w,h,-d/2,th)
    buildSide(rootComp,sketch,w,h,d/2,th)
    
    sketch = addYZPlane(rootComp)
    buildSide(rootComp,sketch,d,h,-w/2,th)
    buildSide(rootComp,sketch,d,h,w/2,th)
    
    sketch = addXZPlane(rootComp)
    buildSide(rootComp,sketch,w,d,-h/2,th)
    buildSide(rootComp,sketch,w,d,h/2,th)
   
# gets the XY plane and adds it to sketch, so we can generalize the profile-building
def addXYPlane(rootComp):
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    return sketch

# gets the XY plane and adds it to sketch, so we can generalize the profile-building
def addYZPlane(rootComp):
    sketches = rootComp.sketches
    yzPlane = rootComp.yZConstructionPlane
    sketch = sketches.add(yzPlane)
    return sketch

# gets the XY plane and adds it to sketch, so we can generalize the profile-building
def addXZPlane(rootComp):
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane
    sketch = sketches.add(xzPlane)
    return sketch
    

#def buildSide(rootComp, sketch, sideStr, x,y,z,th):
def buildSide(rootComp, sketch, px, py, offset,th): 
    try:
        # Draw two connected lines.
        lines = sketch.sketchCurves.sketchLines;
        lineArr = []
        lineArr.append(lines.addByTwoPoints(adsk.core.Point3D.create(-px/2, -py/2, offset), adsk.core.Point3D.create(px/2, -py/2, offset)))
        lineArr.append(lines.addByTwoPoints(lineArr[0].endSketchPoint, adsk.core.Point3D.create(px/2, py/2, offset)))
        lineArr.append(lines.addByTwoPoints(lineArr[1].endSketchPoint, adsk.core.Point3D.create(-px/2, py/2, offset)))
        lineArr.append(lines.addByTwoPoints(lineArr[2].endSketchPoint, adsk.core.Point3D.create(-px/2, -py/2, offset)))   
        extrudeSketch(rootComp,sketch,th)
       
    except Exception as error:
        getUI().messageBox('Failed : ' + str(error))     


def extrudeSketch(rootComp,sketch,th):
        # Get the profile defined by item#0.
        prof = sketch.profiles.item(0)
        
        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extrudes = rootComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)
        
        # Define that the extent of the thickness        
        distance = adsk.core.ValueInput.createByReal(th)
        extInput.setDistanceExtent(False, distance)
        
         # Create the extrusion.
        ext = extrudes.add(extInput)

def getUI():
    app = adsk.core.Application.get()
    ui = app.userInterface
    return ui
    
def main():
    ui = None
    try: 
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        design = app.activeProduct
        if not design:
            ui.messageBox('No active Fusion design', 'No Design')
            return

        # Get the root component of the active design.
        rootComp = design.rootComponent
        
        # get input from user here
        w = 12  # x = 120mm
        h = 6   # y = 60mm
        d = 3   # z = 30mnm
        th = .1
        buildBox(rootComp, w,h,d,th)
    except Exception as error:
        ui.messageBox('Failed : ' + str(error))     
        

main()