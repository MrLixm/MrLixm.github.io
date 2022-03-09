-- pseudo code to showcase code logic, not usable as it is

local data = Interface.GetAttr("geometry.point.P")

local samples local sample
local values
local new_value = {}

--[[ --------------------------------------------------------------------------
  USING TABLES

  table are a bit faster but can only go up to 2^27 (134 million) values per attribute

]]

samples = data:getNumberOfTimeSamples()

for smplindex=0, samples - 1 do
  -- convert the smplindex to sampletime (shutterOpen/Close values)
  sample = data:getSampleTime(smplindex)
  values = data:getNearestSample(sample) -- table
  -- // do something with the values table
  new_value[sample] = values
end

--[[ --------------------------------------------------------------------------
  USING ARRAYS

  arrays are a bit slower but have no limit,
  array manipulation is less convenient than tables.

]]

samples = data:getSamples()

for smplindex=0, #samples - 1 do
  sample = samples:get(smplindex) -- get() starts at 0
  values = sample:toArray() -- Array
  -- // do something with the values Array
  new_value[sample:getSampleTime()] = values
end

-- new value is a table of time samples. Exemple :
-- new_value {-0.25={...}, 0.0={...}, 0.25={...}}
-- new_value {-0.25=Array, 0.0=Array, 0.25=Array}
