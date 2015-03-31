#Author-Scott Kildall
#Description-Create a finger-joint box.

import adsk.core, adsk.fusion, traceback
import os, math

# global set of event handlers to keep them referenced for the duration of the command
handlers = []

app = adsk.core.Application.get()
if app:
    ui = app.userInterface

defaultWidth = 12
defaultHeight = 6
defaultDepth = 3
defaultThickness = .1

newComp = None

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component


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

#---- FJBOx -- END
class FJBoxCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            widthInput = 0
            heightInput = 0
            depthInput = 0
            thicknessInput = 0

            # We need access to the inputs within a command during the execute.
            for input in inputs:
                if input.id == 'widthInput':
                    widthInput = input
                elif input.id == 'heightInput':
                    heightInput = input
                elif input.id == 'depthInput':
                    depthInput = input
                elif input.id == 'thicknessInput':
                    thicknessInput = input

            width = 0
            height = 0
            depth = 0
            thickness = 0

            if not widthInput or not heightInput or not depthInput or not thicknessInput:
                ui.messageBox("One of the inputs don't exist.")

                width = defaultWidth
                height = defaultHeight
                depth = defaultDepth
                thickness = defaultThickness
            else:
                width = unitsMgr.evaluateExpression(widthInput.expression, "cm")
                height = unitsMgr.evaluateExpression(heightInput.expression, "cm")
                depth = unitsMgr.evaluateExpression(depthInput.expression, "cm")
                thickness = unitsMgr.evaluateExpression(thicknessInput.expression, "cm")
            
            design = app.activeProduct
            if not design:
                ui.messageBox('No active Fusion design', 'No Design')
                return
            
            # Get the root component of the active design.
            rootComp = design.rootComponent
        
            # build from user input
            buildBox(rootComp, width,height,depth,thickness)
        
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FJBoxCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FJBoxCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = FJBoxCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onDestroy = FJBoxCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onDestroy)

            # Define the inputs.
            inputs = cmd.commandInputs

            initialVal = adsk.core.ValueInput.createByReal(defaultWidth)
            inputs.addValueInput('widthInput', 'Width (cm)', 'cm' , initialVal)

            initialVal2 = adsk.core.ValueInput.createByReal(defaultHeight)
            inputs.addValueInput('heightInput', 'Height (cm)', 'cm' , initialVal2)
            
            initialVal3 = adsk.core.ValueInput.createByReal(defaultDepth)
            inputs.addValueInput('depthInput', 'Depth (cm)', 'cm' , initialVal3)
            
            initialVal4 = adsk.core.ValueInput.createByReal(defaultThickness)
            inputs.addValueInput('thicknessInput', 'Wall Thickness', 'cm' , initialVal4)


        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))





def main():
    try:
        commandId = 'FJBox'
        commandName = 'Create Finger-Joint Box'
        commandDescription = 'Create a finger-joint box'
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            resourceDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources') # absolute resource file path is specified
            cmdDef = ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription, resourceDir)

        onCommandCreated = FJBoxCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)

        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

main()
