using CSV
using Plots
using DataFrames
using PlutoUI

function read_df(path)
    d = DataFrame(
                  N = Int[],
                  Z = Int[],
                  A = Int[],
                  binding_energy = Float32[],
                  binding_energy_per_nucleon = Float32[],
                  )
    row = 0
    start = 40
    a = -1
    for line in eachline(open(path))
        row += 1
        if row < start
            continue
        end
        n = parse(Int, line[7:9])
        z = parse(Int, line[12:14])
        # a can be empty (It is only there if it differs from the last a)
        # It looks like 1 - - - 2 - - - 3 ... (- mark lines)
        a_ = tryparse(Int, line[17:19])
        a = isnothing(a_) ? a : a_
        #a = tryparse(Int, line[17:19])
        # sometimes # is used instead of .
        # for this purpose we consider them equal
        b_e = parse(Float32, replace(line[49:60], "#" => "."))
        push!(d, [n, z, a, b_e, b_e/a])
    end
    d
end

function max_binding_energy(df, col)
    gdf = groupby(df, col)
    combine(gdf, :binding_energy_per_nucleon => maximum)
end


df = read_df("data")
max_bindings = max_binding_energy(df, "A")
A = max_bindings.A
E = max_bindings.binding_energy_per_nucleon_maximum
highlights = [1,4,8,12,16,56]
text_y = E[highlights]
y_ = 7800
upper = text_y .> y_
under = text_y .< y_ 
text_y[upper] = text_y[upper] .- 600
text_y[under] = text_y[under] .+ 500
p = plot(
         A,
         E,
         xscale=:log,
         label="",
         xlabel="A = Z + N",
         ylabel="Binding Energy / A [kEV]",
         )
scatter!(
         A[highlights],
         E[highlights],
         label="",
         markersize=6,
         markershape=:star4,
         )
annotate!(
          highlights,
          text_y,
          # these have to be filled manually because I didnt bother reading them
          ["¹H", "⁴HE", "⁸Be", "¹²C  ", "  ¹⁶O", "⁵⁶FE"],
          )

savefig(p, "binding_energy.png")
savefig(p, "binding_energy.svg")
