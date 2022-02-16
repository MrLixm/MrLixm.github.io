--[[
OpScript for Foundry's Katana software

Author: Mixed sources
Modified by: Liam Collod
Last Modified: 28/04/2021

[OpScript setup]
  user variables:
    "user.instanceSourceLocations" string array (Scene graph locations)
    "user.pointCloudLocation" string, scene graph location to the pointcloud
  parameters:
    applyWhere: at specific location
    location: desired output locations for the instances created

[License]
Array Instancing Opscript for Katana
Copyright (C) 2022  Liam Collod

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
]]

-- version = "4.0.4" Rotation degree to radian version

function clamp(value, min, max)
  return math.min(math.max(value, min), max)
end


function value_conform(value)
  -- make sure a value is above 0
  if value < 0 then
    return clamp(value * -1, 0.0, 1.0)
  else
    return value
  end
end

function set_rotation_table_order(rotation_table, current_index, axis)
  if axis == "x" then
    rotation_table[current_index*4+2] = 1.0
    rotation_table[current_index*4+3] = 0.0
    rotation_table[current_index*4+4] = 0.0
  elseif axis == "y" then
    rotation_table[current_index*4+2] = 0.0
    rotation_table[current_index*4+3] = 1.0
    rotation_table[current_index*4+4] = 0.0
  elseif axis == "z" then
    rotation_table[current_index*4+2] = 0.0
    rotation_table[current_index*4+3] = 0.0
    rotation_table[current_index*4+4] = 1.0
  else
    Interface.ReportWarning("Unsuported axis parameters: "..axis)
  end
end

function degree_to_radian(rotation)
  return rotation * math.pi/180.0
end


--[[ --------------------------------------------------------------------------
INSTANCING
]]

-- Define the name of the attributes exported in the point cloud
-- comment the assignation line to disable theire utilisation
local rotation_attr_name
rotation_attr_name = "protation"

local scale_attr_name
scale_attr_name = "pscale"

local id_attr_name
id_attr_name= "pinstanceID"

local id_offset = 0 -- 1 if the id_attr start at 1 instead of 0

local random_color_attr_name
random_color_attr_name = "pcolorRdm"


local currentTime = Interface.GetCurrentTime()

-- Read User arguments
local userSourceLocations = Interface.GetOpArg("user.instanceSourceLocations")
local pointCloudLocation = Interface.GetOpArg("user.pointCloudLocation"):getValue()

local pc_points
local pc_rotations
local pc_scales
local scaleValueType
local pc_ids
local pc_rdmColor

-- # Read the point cloud point attributes
-- table
pc_points = Interface.GetAttr(
   "geometry.point.P",
   pointCloudLocation):getNearestSample(currentTime)

if rotation_attr_name then
  -- table
  pc_rotations = Interface.GetAttr(
     "geometry.arbitrary."..rotation_attr_name..".value",
     pointCloudLocation)  :getNearestSample(currentTime)
end

if scale_attr_name then
  -- table
  pc_scales = Interface.GetAttr(
     "geometry.arbitrary."..scale_attr_name..".value",
     pointCloudLocation):getNearestSample(currentTime)

  -- We get the type of the attribute to know if it need to be converted
  local scale_attr = Interface.GetAttr(
      "geometry.arbitrary."..scale_attr_name..".inputType",
      pointCloudLocation)

  if scale_attr then
    scaleValueType = scale_attr:getNearestSample(currentTime)
  else
    scaleValueType = false
  end

end

if id_attr_name then
  -- table
  pc_ids = Interface.GetAttr(
     "geometry.arbitrary."..id_attr_name..".value",
     pointCloudLocation):getNearestSample(currentTime)
end

if random_color_attr_name then
  pc_rdmColor = Interface.GetAttr(
    "geometry.arbitrary."..random_color_attr_name..".value",
    pointCloudLocation)  :getNearestSample(currentTime)
end

--[[ --------------------------------------------------------------------------
  Build the InstanceArray attributes
]]

local instanceTranslate = {}
local instanceRotation = {}
local instanceScale = {}
local instance_rx = {}
local instance_ry= {}
local instance_rz = {}
local instanceIndex = {}
local instanceRdmColor = {}


-- Start looping through the points
for i=0, (#pc_points /3 - 1) do

  instanceTranslate[3*i+1] = pc_points[3*i+1]
  instanceTranslate[3*i+2] = pc_points[3*i+2]
  instanceTranslate[3*i+3] = pc_points[3*i+3]

  if pc_rotations then
    instance_rx[i*4+1] = degree_to_radian(pc_rotations[3*i+1])
    set_rotation_table_order(instance_rx,i,"x")
    instance_ry[i*4+1] = degree_to_radian(pc_rotations[3*i+2])
    set_rotation_table_order(instance_ry,i,"y")
    instance_rz[i*4+1] = degree_to_radian(pc_rotations[3*i+3])
    set_rotation_table_order(instance_rz,i,"z")
  else
    instance_rx[i*4+1] = 0.0
    set_rotation_table_order(instance_rx,i,"x")
    instance_ry[i*4+2] = 0.0
    set_rotation_table_order(instance_ry,i,"y")
    instance_rz[i*4+3] = 0.0
    set_rotation_table_order(instance_rz,i,"z")
  end

  if pc_scales then
    if scaleValueType then
      instanceScale[i*3+1] = pc_scales[3*i+1]
      instanceScale[i*3+2] = pc_scales[3*i+2]
      instanceScale[i*3+3] = pc_scales[3*i+3]
    else
      instanceScale[i*3+1] = pc_scales[i+1]
      instanceScale[i*3+2] = pc_scales[i+1]
      instanceScale[i*3+3] = pc_scales[i+1]
    end
  else
    instanceScale[i*3+1] = 1.0
    instanceScale[i*3+2] = 1.0
    instanceScale[i*3+3] = 1.0
  end

  if pc_rdmColor then
    instanceRdmColor[i*3+1] = value_conform(pc_rdmColor[3*i+1])
    instanceRdmColor[i*3+2] = value_conform(pc_rdmColor[3*i+2])
    instanceRdmColor[i*3+3] = value_conform(pc_rdmColor[3*i+3])
  else
    instanceRdmColor[i*3+1] = 1.0
    instanceRdmColor[i*3+2] = 1.0
    instanceRdmColor[i*3+3] = 1.0
  end

  if pc_ids then
    instanceIndex[i+1] = pc_ids[i+1] - id_offset
  else
    instanceIndex[i+1] = 0
  end

end

--[[ --------------------------------------------------------------------------
  Set the InstanceArray attributes
]]

Interface.SetAttr('type', StringAttribute('instance array'))
Interface.SetAttr('geometry.instanceSource', userSourceLocations)
Interface.SetAttr('geometry.instanceIndex', IntAttribute(instanceIndex, 1))
Interface.SetAttr('geometry.instanceTranslate',
                  DoubleAttribute(instanceTranslate, 3))
Interface.SetAttr('geometry.instanceRotateX', DoubleAttribute(instance_rx, 4))
Interface.SetAttr('geometry.instanceRotateY', DoubleAttribute(instance_ry, 4))
Interface.SetAttr('geometry.instanceRotateZ', DoubleAttribute(instance_rz, 4))
Interface.SetAttr('geometry.instanceScale', DoubleAttribute(instanceScale, 3))
Interface.SetAttr('instance.arbitrary.randomColor',
                  FloatAttribute(instanceRdmColor, 3))
