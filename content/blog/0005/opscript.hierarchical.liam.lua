--[[
  OpScript for Foundry's Katana software

  Author: Mixed sources
  Modified by: Liam Collod
  Last Modified: 11/06/2021 (added proxy)

  [OpScript setup]
    user variables:
      "user.instanceSourceLocations" string array (Scene graph locations)
      "user.pointCloudLocation" string, scene graph location to the pointcloud
    parameters:
      applyWhere: at specific location
      location: desired output locations for the instances created
]]

-- version = "0.3.6"

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


function get_proxy_path(proxy_path_attr)

  if not proxy_path_attr then
    return
  end
  local proxy_path_value = proxy_path_attr:getNearestSample(Interface.GetCurrentTime())
  return proxy_path_value
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


if Interface.AtRoot() then

  local currentTime = Interface.GetCurrentTime()


  -- Read User arguments
  local userSourceLocations = Interface.GetOpArg("user.instanceSourceLocations")
  local pointCloudLocation = Interface.GetOpArg("user.pointCloudLocation"):getValue()
  local instanceSourceLocations = userSourceLocations:getNearestSample(
                  currentTime)
  local previewEnable = Interface.GetOpArg("user.previewEnable")
  local proxy_path

  local points
  local rotatePP
  local scalePP
  local scaleValueType
  local idPP
  local random_color
  local visiblePP

  -- # Read the point cloud point attributes
  -- table
  points = Interface.GetAttr(
     "geometry.point.P",
     pointCloudLocation):getNearestSample(currentTime)

  if rotation_attr_name then
    -- table
    rotatePP = Interface.GetAttr(
       "geometry.arbitrary."..rotation_attr_name..".value",
       pointCloudLocation):getNearestSample(currentTime)
  end

  if scale_attr_name then
    -- table
    scalePP = Interface.GetAttr(
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
    idPP = Interface.GetAttr(
       "geometry.arbitrary."..id_attr_name..".value",
       pointCloudLocation):getNearestSample(currentTime)
  end

  if random_color_attr_name then
    random_color = Interface.GetAttr(
      "geometry.arbitrary."..random_color_attr_name..".value",
      pointCloudLocation):getNearestSample(currentTime)
  end


  local x, y, z
  local rx, ry, rz
  local sx, sy, sz
  local instanceSourceLocation
  local cd_r, cd_g, cd_b
  local current_id
  local asset_name
  local asset_names_table = {} -- to avoid string concatenation in loop
  local gb
  local _ -- garbage variable

  local stime = os.clock()
  -- Start looping through the points
  for i=0, (#points/3 - 1) do

    gb = GroupBuilder()

    x = points[3*i+1]
    y = points[3*i+2]
    z = points[3*i+3]

    if rotatePP then
      rx = rotatePP[3*i+1]
      ry = rotatePP[3*i+2]
      rz = rotatePP[3*i+3]
    else
      rx = 0.0
      ry = 0.0
      rz = 0.0
    end

    if scalePP then
      if scaleValueType then
        sx = scalePP[3*i+1]
        sy = scalePP[3*i+2]
        sz = scalePP[3*i+3]
      else
        sx = scalePP[i+1]
        sy = scalePP[i+1]
        sz = scalePP[i+1]
      end
    else
      sx = 1.0
      sy = 1.0
      sz = 1.0
    end

    if random_color then
      cd_r = value_conform(random_color[3*i+1])
      cd_g = value_conform(random_color[3*i+2])
      cd_b = value_conform(random_color[3*i+3])
    else
      cd_r = 1.0
      cd_g = 1.0
      cd_b = 1.0
    end

    if idPP then
      current_id = idPP[i+1] - id_offset
      instanceSourceLocation = instanceSourceLocations[current_id + 1]
      if not instanceSourceLocation then
        Interface.ReportWarning("No instance_source_location find.")
      end
    else
        instanceSourceLocation = instanceSourceLocations[1] -- string: CEL
    end

    -- Build op arguments for the child location
    gb:update(Interface.GetOpArg())

    gb:set("childAttrs", Interface.GetAttr("", instanceSourceLocation))
    gb:set("childAttrs.type", StringAttribute("instance"))
    gb:set("childAttrs.geometry.instanceSource",
        StringAttribute(instanceSourceLocation))
    -- translate
    gb:set("childAttrs.xform.interactive.translate",
        DoubleAttribute({x, y, z}))
    -- rotation
    gb:set("childAttrs.xform.interactive.rotateZ",
        DoubleAttribute({rz, 0.0, 0.0, 1.0}))
    gb:set("childAttrs.xform.interactive.rotateY",
        DoubleAttribute({ry, 0.0, 1.0, 0.0}))
    gb:set("childAttrs.xform.interactive.rotateX",
        DoubleAttribute({rx, 1.0, 0.0, 0.0}))
    -- scale
    gb:set("childAttrs.xform.interactive.scale",
        DoubleAttribute({sx, sy, sz}))

    -- specific to Redshift (at instance.arbitrary)
    gb:set("childAttrs.instance.arbitrary.randomColor", FloatAttribute({
      cd_r, cd_g, cd_b}, 3))

    _, asset_name = instanceSourceLocation:match("([^,]+)/([^,]+)")
    if not asset_name then
      asset_name = "instance"
    end
    -- to avoid string concatenation in loop
    asset_names_table[1] = asset_name
    asset_names_table[2] = string.format("_%08d", i)

    -- [[ proxy setup for viewer
    if previewEnable:getNearestSample(currentTime)[1] == 1 then
      local instanceSourceAbcPathAttr = Interface.GetAttr(
          "asset.abc_path",
          instanceSourceLocations[current_id + 1]
      )
      proxy_path = get_proxy_path(instanceSourceAbcPathAttr)

      if proxy_path then
        gb:set("childAttrs.proxies.viewer", StringAttribute(proxy_path))
      end

    end
    -- end proxy setup ]]

    -- Create the child
    Interface.CreateChild(
        table.concat(asset_names_table),
        Interface.GetOpType(),
        gb:build())

  -- if the point is not visible just continue
  end
  print("Loop finished in "..os.clock()-stime)

else
  local childAttrs = Interface.GetOpArg("childAttrs")

  for i=0, childAttrs:getNumberOfChildren()-1 do

      Interface.SetAttr(childAttrs:getChildName(i), childAttrs:getChildByIndex(i))

  end
end
