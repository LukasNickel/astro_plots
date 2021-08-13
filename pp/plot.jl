### A Pluto.jl notebook ###
# v0.15.1

using Markdown
using InteractiveUtils

# ╔═╡ 8f9a3074-f92f-11eb-33dd-41eeab6f1ece
using Pkg

# ╔═╡ 15d15589-759d-4490-91dd-033f0eff550e
Pkg.add("LightGraphs")

# ╔═╡ 50dbc3e2-cbdf-470a-b71b-488a8423877b
begin
	Pkg.add("PyPlot")
end

# ╔═╡ c3cd9a02-a051-49be-a558-b57ecedbad5d
using GraphRecipes

# ╔═╡ 33e4b886-01f1-4438-889b-f4ebdefed9ce
using LightGraphs

# ╔═╡ 79a55dae-cd3e-4f90-9973-b710c744b6a6
using GraphPlot

# ╔═╡ 78cc9dcf-50d8-4284-9669-7323a05cd8f1
using Plots

# ╔═╡ 2ac3ef7b-7a9c-42c9-ae49-694094cbba10
#pgfplotsx()

# ╔═╡ 29f9ee4a-40a1-406a-bcdd-d763165a4e48
pyplot()

# ╔═╡ 2b807a12-be01-4dee-82f0-55e8e538406a
positions = [
	0 0;
	-1 1;
	1 1
]

# ╔═╡ 0bca08d0-20d5-4b2f-b682-7e4b3f7c9c78
n=3

# ╔═╡ 64cd57ea-3146-4d05-9e40-d9111971c502
pp = Dict(
	:a => Dict(
		:b => 1,
		:c => 2
	)
)

# ╔═╡ 7832eb0c-35fa-49c7-8ec4-e75059314d0c
const A = Float64[ rand() < 0.5 ? 0 : rand() for i=1:n, j=1:n]

# ╔═╡ abb9e1b1-20b2-4f6b-a374-a1d9bd67ae93
names = ["A", "B", "C"]

# ╔═╡ a046ced9-90b7-47c0-bf42-f5b1c50d2ca1
begin
	nvertices = 15
	G1 = Graph(nvertices)
	labels = [
		"¹H+¹H → ²H + e",
		"¹H+¹H+e → ²H",
		"²H+H → ³H",
		"³He + ³He → ⁴He + 2 ¹H",
		"³He + ⁴He → ⁷Be",
		"³He + ⁴He → ⁷Be",
		"⁷Be + e → ⁷Li + ν_e",
		"⁷Be + ¹H → ⁸B + γ",
		"⁷Li + ¹H -> ⁴He + ⁴He",
		"⁸B -> ⁷Be +e + ν",
		"⁸Be -> ⁴He + ⁴He",
	]
	#labels = ["1a", "b", "c²", "d", "e", "f", "g", "h", "i", "j", "k"]
	edgelabels = Dict()
	x = [
		-1,
		1,
		0,
		-2,
		0,
		2,
		0,
		2,
		0,
		2,
		2
	]
	y = [
		8,
		8,
		6,
		3,
		2,
		3,
		1,
		2,
		0,
		1,
		0
	]


	add_edge!(G1, 1, 3)
	edgelabels[(1,3)] = "99,75%         "
	add_edge!(G1, 2, 3)
	edgelabels[(2,3)] = "    0,25%"
	
	add_edge!(G1, 3, 4)
	edgelabels[(3,4)] = " I\n91%"
	add_edge!(G1, 3, 5)
	edgelabels[(3,5)] = "II\n9%"
	add_edge!(G1, 3, 6)
	edgelabels[(3,6)] = "III\n0.1% "

	add_edge!(G1, 5, 7)
	add_edge!(G1, 6, 8)

	add_edge!(G1, 7, 9)
	add_edge!(G1, 8, 10)

	add_edge!(G1, 10, 11)
end

# ╔═╡ 6d50a9a9-d650-4997-9257-0f4da6136914
plot = graphplot(
	G1,
	names=labels,
	fontsize=10,
	nodeshape=:rect,
	nodesize=0.0,
	x=x,#.*400,
	y=y,#.*400,
	size=(800,1000),
	dpi=100,
	curvature_scalar=0,
	nodecolor=:white,
	shorten=0.1,
	edgelabel=edgelabels,
	edge_label_box=true,
	edgelabel_offset=0.2,
)

# ╔═╡ b7c805b7-cd32-4248-bb8a-5ee067b1183e
typeof(G1)

# ╔═╡ f431b7f9-4c36-4435-85fc-3102e1f2dea7
labels

# ╔═╡ ee189abc-2707-4281-b5cb-73b2890ae023
savefig(plot, "pp.png")

# ╔═╡ ea90e75c-ed5b-48b2-8e7e-f4af4d0d666c
savefig(plot, "pp.svg")

# ╔═╡ 153589fc-5060-4fc2-b6b5-1834450b6847
nv(G1)

# ╔═╡ 7bc0c196-f54b-4c11-8f6e-54ad4636df3d
# set positions manually to avoid randomness!

# ╔═╡ 25cebcd0-a75a-4373-96a6-a0b778fb4f90
savefig(plot, "test.svg")

# ╔═╡ 1d325978-a695-4db9-a55a-353e8b216430
length(labels)

# ╔═╡ cf1815ee-4219-4cac-8225-200b37d13a08
ne(G1)

# ╔═╡ 18247747-32a6-4eb0-87cc-1595c2582e0e
begin
	G2 = Graph(10)
	add_edge!(G2, 1, 3)
	add_edge!(G2, 1, 2)
	
	# first fusion
	add_edge!(G2, 2, 4)
	add_edge!(G2, 3, 4)
	
	# left branch
	add_edge!(G2, 4, 5)
	
	# middle branch
	#add_edge!(G2, 4, 6)

	# right branch
	#add_edge!(G2, 4, 7)
	#x = [0, -1, 1, 0, 0]
	#y = [3, 2, 2, 1, 0]
	#z = [0, 0, 0, 0, 0]
end

# ╔═╡ 054e3631-29b9-45b3-8d62-0ecc5646fe87
graphplot(G2, method=:tree)#, x=x, y=y, z=z)

# ╔═╡ e60e8737-1494-4b34-bc48-ca843c0f17f9
gplot(G2)

# ╔═╡ edf2e096-01e2-4697-8a87-05c188e5b03b


# ╔═╡ 6f7611e6-210a-4b64-b44a-e649b5fb0fa4
a  = Dict()

# ╔═╡ 0e915d78-676f-4e62-b524-72817c48c710
a["1"] = 2

# ╔═╡ 1b44df22-ed90-43ef-a6d5-92f9609b7187
a

# ╔═╡ Cell order:
# ╠═8f9a3074-f92f-11eb-33dd-41eeab6f1ece
# ╠═15d15589-759d-4490-91dd-033f0eff550e
# ╠═c3cd9a02-a051-49be-a558-b57ecedbad5d
# ╠═33e4b886-01f1-4438-889b-f4ebdefed9ce
# ╠═79a55dae-cd3e-4f90-9973-b710c744b6a6
# ╠═78cc9dcf-50d8-4284-9669-7323a05cd8f1
# ╠═2ac3ef7b-7a9c-42c9-ae49-694094cbba10
# ╠═50dbc3e2-cbdf-470a-b71b-488a8423877b
# ╠═29f9ee4a-40a1-406a-bcdd-d763165a4e48
# ╠═2b807a12-be01-4dee-82f0-55e8e538406a
# ╠═0bca08d0-20d5-4b2f-b682-7e4b3f7c9c78
# ╠═64cd57ea-3146-4d05-9e40-d9111971c502
# ╠═7832eb0c-35fa-49c7-8ec4-e75059314d0c
# ╠═abb9e1b1-20b2-4f6b-a374-a1d9bd67ae93
# ╠═a046ced9-90b7-47c0-bf42-f5b1c50d2ca1
# ╠═6d50a9a9-d650-4997-9257-0f4da6136914
# ╠═b7c805b7-cd32-4248-bb8a-5ee067b1183e
# ╠═f431b7f9-4c36-4435-85fc-3102e1f2dea7
# ╠═ee189abc-2707-4281-b5cb-73b2890ae023
# ╠═ea90e75c-ed5b-48b2-8e7e-f4af4d0d666c
# ╠═153589fc-5060-4fc2-b6b5-1834450b6847
# ╠═7bc0c196-f54b-4c11-8f6e-54ad4636df3d
# ╠═25cebcd0-a75a-4373-96a6-a0b778fb4f90
# ╠═1d325978-a695-4db9-a55a-353e8b216430
# ╠═cf1815ee-4219-4cac-8225-200b37d13a08
# ╠═18247747-32a6-4eb0-87cc-1595c2582e0e
# ╠═054e3631-29b9-45b3-8d62-0ecc5646fe87
# ╠═e60e8737-1494-4b34-bc48-ca843c0f17f9
# ╠═edf2e096-01e2-4697-8a87-05c188e5b03b
# ╠═6f7611e6-210a-4b64-b44a-e649b5fb0fa4
# ╠═0e915d78-676f-4e62-b524-72817c48c710
# ╠═1b44df22-ed90-43ef-a6d5-92f9609b7187
