-- this is "pseudo-code", not usable as it is (actually for this one it is).


local pointCloudLocation = Interface.GetOpArg("user.pointCloudLocation"):getValue()

local p_attr = Interface.GetAttr(
    "geometry.point.P",
    pointCloudLocation
)  -- this already return a FloatAttribute instance.


Interface.SetAttr('type', StringAttribute('instance array'))
Interface.SetAttr('geometry.instanceTranslate', p_attr)
