-- this is "pseudo-code", not usable as it is.

local random_color_attr = ...

local points = ...

local instance
local cr, cg, cb

for i=0, #points/3 -1 do

  instance = GroupBuilder()

  --[...]

  cr = random_color_attr[3*i+1]
  cg = random_color_attr[3*i+2]
  cb = random_color_attr[3*i+3]

  -- not gonna lie I don't really know what the scope does
  instance:set(
      "childAttrs.geometry.arbitrary.randomColor.scope",
      StringAttribute("primitive")
  )
  -- inputType is important ! Depends on what node you use in the shading
  -- network to get back the data. In Arnold this would be an `user_data_rgb`
  instance:set(
      "childAttrs.geometry.arbitrary.randomColor.inputType",
      StringAttribute("color3")
  )
  instance:set(
      "childAttrs.geometry.arbitrary.randomColor.value",
       FloatAttribute({cr, cg, cb}, 3)
  )

  Interface.CreateChild(
    instance_name,
    Interface.GetOpType(),
    instance:build()
  )

end
--[...]
