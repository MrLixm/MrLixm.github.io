--[[
source: https://support.foundry.com/hc/en-us/articles/360006999239
]]

-- Read the op arguments
local instanceSourceLocations = Interface.GetOpArg("user.instanceSourceLocations")
local pointCloudLocation = Interface.GetOpArg("user.pointCloudLocation"):getValue()

-- Read the point cloud's points
local pointAttr = Interface.GetAttr("geometry.point.P", pointCloudLocation)
local points = pointAttr:getNearestSample(Interface.GetCurrentTime())


-- declare variable used to build the final instance
-- The indexArray attribute determines which instance source each instance location represents
local indexArray = {}
local matrixArrayMap = {}

--[[---------------------------------------------------------------------------

  PROCESS instance source attribute

]]


-- for each instance create an instance index
for i=0,#points/3-1 do
  -- For this example, the instances are arbitrarily assigned to an
  -- instance source
  -- a more stable apporach would be to use an arbitrary attribute
  -- on the point cloud to assign an instance source
  indexArray[#indexArray+1] = i%instanceSourceLocations:getNumberOfTuples()
end


--[[---------------------------------------------------------------------------

  PROCESS MATRIX ATTRIBUTE

]]
-- Get the transforms from the points
local numTimeSamples = pointAttr:getNumberOfTimeSamples()
local matrixArray
local workMatrix
local sampleTime
local pointSample
local x, y, z
-- to get motion blur on the instances, create an instanceMatrix at each
-- time sample available from the point cloud points attribute
for idx=0,numTimeSamples-1 do
  sampleTime = pointAttr:getSampleTime(idx)
  pointSample = pointAttr:getNearestSample(sampleTime)

  -- each instance in array has its own matrix
  matrixArray = {}
  workMatrix = Imath.M44d():toTable()

  -- for each instance build a matrix with a mocked up transformation
  for i=0,#pointSample/3-1 do
    -- grab the points that represent this instance
    x = pointSample[3*i+1]
    y = pointSample[3*i+2]
    z = pointSample[3*i+3]

    -- set the translate of the matrix to the points in the point cloud
    workMatrix[13] = x
    workMatrix[14] = y
    workMatrix[15] = z

    for j = 1,16 do
      matrixArray[#matrixArray+1]=workMatrix[j]
    end

  end
  matrixArrayMap[sampleTime] = matrixArray

end


--[[---------------------------------------------------------------------------

 Build the array instance

]]
-- Create a single location which will generate an array of instances
-- Set type for this location to 'instance array'
Interface.SetAttr('type', StringAttribute('instance array'))
-- This instance array location must point to the instance source locations
-- through the attribute 'geometry.instanceSource'
Interface.SetAttr('geometry.instanceSource', instanceSourceLocations)
-- Set index for instance array element
Interface.SetAttr('geometry.instanceIndex', IntAttribute(indexArray, 1))
Interface.SetAttr('geometry.instanceMatrix', DoubleAttribute(matrixArrayMap, 16))
