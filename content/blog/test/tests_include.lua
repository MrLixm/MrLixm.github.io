--[[
source: https://support.foundry.com/hc/en-us/articles/360006999279
]]

-- Read op arguments
local instanceSourceLocation = Interface.GetOpArg("user.instanceSourceLocation"):getValue()
local pointCloudLocation = Interface.GetOpArg("user.pointCloudLocation"):getValue()

if Interface.AtRoot() then
  -- Read the point cloud
  local points = Interface.GetAttr("geometry.point.P", pointCloudLocation)
  points = points:getNearestSample(Interface.GetCurrentTime())

  -- Loop over points
  local x, y, z
  local gb = GroupBuilder()
  for i=0, #points/3 - 1 do
    x = points[3*i+1]
    y = points[3*i+2]
    z = points[3*i+3]

    -- Build op arguments for the child location
    gb:update(Interface.GetOpArg())
    gb:set("childAttrs", Interface.GetAttr("", instanceSourceLocation))
    gb:set("childAttrs.type", StringAttribute("instance"))
    gb:set("childAttrs.geometry.instanceSource", StringAttribute(instanceSourceLocation))
    gb:set("childAttrs.xform.interactive.translate", DoubleAttribute({x, y, z}))
  end
end
  -- missing code !!! Only for test purposes !!!
