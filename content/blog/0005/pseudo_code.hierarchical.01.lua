-- this is "pseudo-code", not usable as it is.
local points = ...

local translate_attr = ...
local rotate_attr = ...
local scale_attr = ...

local out_translate
local out_rotateX
local out_rotateY
local out_rotateZ
local out_scale

local instance

-- points is divided by 3 cause it has `num point * XYZ`
-- in lua we start counting at 1 but we need the `i` to start at 0 to correctly
-- gather each point index. As we start at 0 we remove 1 to compensate.
for i=0, #points/3 -1 do

  instance = GroupBuilder()

  out_translate = {points[3*i+1], points[3*i+2], points[3*i+3]}
  -- as stated in the doc, rotations need to define axis orientation.
  out_rotateX = {rotate_attr[3*i+1], 1.0, 0.0, 0.0}
  out_rotateY = {rotate_attr[3*i+2], 0.0, 1.0, 0.0}
  --[...]

  --[...]
  instance:set("childAttrs.xform.group0.translate", out_translate)
  instance:set("childAttrs.xform.group0.rotateZ", out_rotateX)
  instance:set("childAttrs.xform.group0.rotateY", out_rotateY)
  instance:set("childAttrs.xform.group0.rotateX", out_rotateZ)
  instance:set("childAttrs.xform.group0.scale", out_scale)

  Interface.CreateChild(
    instance_name,
    Interface.GetOpType(),
    instance:build()
  )

end
--[...]
