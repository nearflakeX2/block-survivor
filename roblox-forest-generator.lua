-- Roblox Forest Generator
-- Paste into a Script in ServerScriptService, then run Play.

local Workspace = game:GetService("Workspace")
local Terrain = Workspace:FindFirstChildOfClass("Terrain")

-- ===== Config =====
local FOREST_CENTER = Vector3.new(0, 0, 0)
local FOREST_SIZE = Vector2.new(900, 900) -- XZ size in studs
local TREE_COUNT = 420
local ROCK_COUNT = 120
local BUSH_COUNT = 220
local CLEAR_EXISTING_FOREST = true
local SEED = 1337

local BIOME = {
	groundMaterial = Enum.Material.Grass,
	pathMaterial = Enum.Material.Ground,
	treeTrunkColor = Color3.fromRGB(88, 58, 37),
	treeLeafColor = Color3.fromRGB(46, 115, 58),
	bushColor = Color3.fromRGB(52, 129, 66),
	rockColor = Color3.fromRGB(105, 109, 112)
}

-- ===== Utilities =====
local rng = Random.new(SEED)

local function randRange(min, max)
	return min + rng:NextNumber() * (max - min)
end

local function randXZInForest()
	local halfX = FOREST_SIZE.X * 0.5
	local halfZ = FOREST_SIZE.Y * 0.5
	local x = FOREST_CENTER.X + randRange(-halfX, halfX)
	local z = FOREST_CENTER.Z + randRange(-halfZ, halfZ)
	return x, z
end

local function getGroundY(x, z)
	local origin = Vector3.new(x, FOREST_CENTER.Y + 800, z)
	local direction = Vector3.new(0, -2000, 0)
	local result = Workspace:Raycast(origin, direction)
	if result then
		return result.Position.Y
	end
	return FOREST_CENTER.Y
end

local function makePart(parent, size, cframe, material, color, shape)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = true
	p.Size = size
	p.CFrame = cframe
	p.Material = material
	p.Color = color
	if shape then p.Shape = shape end
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

-- ===== Setup folders =====
local forestFolder = Workspace:FindFirstChild("GeneratedForest")
if forestFolder and CLEAR_EXISTING_FOREST then
	forestFolder:Destroy()
	forestFolder = nil
end

if not forestFolder then
	forestFolder = Instance.new("Folder")
	forestFolder.Name = "GeneratedForest"
	forestFolder.Parent = Workspace
end

local treesFolder = Instance.new("Folder")
treesFolder.Name = "Trees"
treesFolder.Parent = forestFolder

local decoFolder = Instance.new("Folder")
decoFolder.Name = "Decoration"
decoFolder.Parent = forestFolder

-- ===== Ground patch (optional terrain paint fallback) =====
local ground = makePart(
	forestFolder,
	Vector3.new(FOREST_SIZE.X, 4, FOREST_SIZE.Y),
	CFrame.new(FOREST_CENTER.X, FOREST_CENTER.Y - 2, FOREST_CENTER.Z),
	BIOME.groundMaterial,
	Color3.fromRGB(76, 125, 67)
)
ground.Name = "ForestGround"

-- ===== Path carving (simple winding path) =====
local pathFolder = Instance.new("Folder")
pathFolder.Name = "Paths"
pathFolder.Parent = forestFolder

local pathPoints = 28
local pathWidth = 18
local prevPos
for i = 1, pathPoints do
	local t = (i - 1) / (pathPoints - 1)
	local x = FOREST_CENTER.X - FOREST_SIZE.X * 0.45 + t * FOREST_SIZE.X * 0.9
	local z = FOREST_CENTER.Z + math.sin(t * math.pi * 2.2) * (FOREST_SIZE.Y * 0.22) + randRange(-14, 14)
	local y = getGroundY(x, z) + 0.2
	local current = Vector3.new(x, y, z)

	if prevPos then
		local mid = (prevPos + current) * 0.5
		local dist = (current - prevPos).Magnitude
		local pathPiece = makePart(
			pathFolder,
			Vector3.new(pathWidth, 1.2, dist),
			CFrame.lookAt(mid, current) * CFrame.Angles(math.rad(90), 0, 0),
			BIOME.pathMaterial,
			Color3.fromRGB(95, 84, 64)
		)
		pathPiece.Name = "Path"
	end

	prevPos = current
end

local function nearPath(x, z)
	for _, p in ipairs(pathFolder:GetChildren()) do
		if p:IsA("Part") then
			local localPos = p.CFrame:PointToObjectSpace(Vector3.new(x, p.Position.Y, z))
			if math.abs(localPos.X) <= (p.Size.X * 0.55) and math.abs(localPos.Z) <= (p.Size.Z * 0.55) then
				return true
			end
		end
	end
	return false
end

-- ===== Tree generation =====
for i = 1, TREE_COUNT do
	local x, z = randXZInForest()
	if not nearPath(x, z) then
		local y = getGroundY(x, z)
		local trunkH = randRange(16, 30)
		local trunkR = randRange(1.2, 2.3)
		local canopyR = randRange(6, 11)

		local model = Instance.new("Model")
		model.Name = "Tree_" .. i
		model.Parent = treesFolder

		local trunk = makePart(
			model,
			Vector3.new(trunkR * 2, trunkH, trunkR * 2),
			CFrame.new(x, y + trunkH * 0.5, z) * CFrame.Angles(0, math.rad(randRange(0, 360)), 0),
			Enum.Material.Wood,
			BIOME.treeTrunkColor,
			Enum.PartType.Cylinder
		)
		trunk.Name = "Trunk"

		local canopy = makePart(
			model,
			Vector3.new(canopyR * 2.2, canopyR * 1.8, canopyR * 2.2),
			CFrame.new(x, y + trunkH + canopyR * 0.45, z),
			Enum.Material.Grass,
			BIOME.treeLeafColor,
			Enum.PartType.Ball
		)
		canopy.Name = "Canopy"

		-- Small secondary canopy for more natural shape
		local canopy2Offset = Vector3.new(randRange(-2.5, 2.5), randRange(2, 5), randRange(-2.5, 2.5))
		local canopy2Scale = randRange(0.5, 0.8)
		local canopy2 = makePart(
			model,
			Vector3.new(canopyR * 2.2, canopyR * 1.8, canopyR * 2.2) * canopy2Scale,
			CFrame.new(x, y + trunkH + canopyR * 0.45, z) + canopy2Offset,
			Enum.Material.Grass,
			BIOME.treeLeafColor:Lerp(Color3.new(0,0,0), 0.06),
			Enum.PartType.Ball
		)
		canopy2.Name = "Canopy2"
	end
end

-- ===== Rocks =====
for i = 1, ROCK_COUNT do
	local x, z = randXZInForest()
	local y = getGroundY(x, z)
	local sx = randRange(2, 8)
	local sy = randRange(1.5, 5)
	local sz = randRange(2, 7)
	local rock = makePart(
		decoFolder,
		Vector3.new(sx, sy, sz),
		CFrame.new(x, y + sy * 0.42, z) * CFrame.Angles(math.rad(randRange(0, 22)), math.rad(randRange(0, 360)), math.rad(randRange(0, 22))),
		Enum.Material.Slate,
		BIOME.rockColor
	)
	rock.Name = "Rock_" .. i
end

-- ===== Bushes =====
for i = 1, BUSH_COUNT do
	local x, z = randXZInForest()
	if not nearPath(x, z) then
		local y = getGroundY(x, z)
		local r = randRange(1.7, 4.6)
		local bush = makePart(
			decoFolder,
			Vector3.new(r * 2.2, r * 1.2, r * 2.2),
			CFrame.new(x, y + r * 0.35, z),
			Enum.Material.Grass,
			BIOME.bushColor,
			Enum.PartType.Ball
		)
		bush.Name = "Bush_" .. i
	end
end

print("[Forest Generator] Done. GeneratedForest created with trees, rocks, bushes, and paths.")
