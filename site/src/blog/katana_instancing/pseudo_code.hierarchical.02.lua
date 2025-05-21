-- this is "pseudo-code", not usable as it is.

local user_instance_sources = ...

local points = ...
local instance_index_attr = ...

local instance
local out_instance_source
local current_instance_index

for i=0, #points/3 -1 do

  instance = GroupBuilder()

  -- find which index the currently visited point corresponds to
  current_instance_index =  instance_index_attr[i+1]
  -- The user_instance_sources had of course to be submitted in the proper
  -- order to work.
  -- (in lua, we start counting from 1, so if the above index returned start
  -- at 0, we need to add 1.)
  out_instance_source = user_instance_sources[current_instance_index + 1]

  instance:set(
      "childAttrs.geometry.instanceSource",
      StringAttribute(out_instance_source)
  )
  --[...]

  Interface.CreateChild(
    instance_name,
    Interface.GetOpType(),
    instance:build()
  )

end
--[...]
