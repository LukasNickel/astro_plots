using Unitful
using PlutoUI
using PhysicalConstants.CODATA2018
using Plots
using Printf

k_B = BoltzmannConstant
c_0 = SpeedOfLightInVacuum
h = PlanckConstant


function planck_spectrum(lambdas, T)
	res = []
	for λ in lambdas
		push!(
			res,
			ustrip(
				uconvert(
					u"W/m^3", 2*pi*h*c_0^2 / λ.^5 / (exp(h*c_0/λ/k_B/T) - 1))
				)
			)
	end
	return res
end

function add_visible_light(lambda_unit, height, alpha)
	bar!(
		[ustrip(uconvert(lambda_unit, 400u"nm"))],
		[height],
		fillcolor=[:violet],
		bar_width=ustrip(uconvert(lambda_unit, 40u"nm")),
		fillalpha=alpha,
		label="",
	)
	bar!(
		[ustrip(uconvert(lambda_unit, 455u"nm"))],
		[height],
		fillcolor=[:blue],
		bar_width=ustrip(uconvert(lambda_unit, 70u"nm")),
		fillalpha=alpha,
		label="",
	)
	bar!(
		[ustrip(uconvert(lambda_unit, 532.5u"nm"))],
		[height],
		fillcolor=[:green],
		bar_width=ustrip(uconvert(lambda_unit, 85u"nm")),
		fillalpha=alpha,
		label="",
	)
	bar!(
		[ustrip(uconvert(lambda_unit, 580u"nm"))],
		[height],
		fillcolor=[:yellow],
		bar_width=ustrip(uconvert(lambda_unit, 10u"nm")),
		fillalpha=alpha,
		label="",
	)
	bar!(
		[ustrip(uconvert(lambda_unit, 617.5u"nm"))],
		[height],
		fillcolor=[:orange],
		bar_width=ustrip(uconvert(lambda_unit, 65u"nm")),
		fillalpha=alpha,
		label="",
	)
	bar!(
		[ustrip(uconvert(lambda_unit, 700u"nm"))],
		[height],
		fillcolor=[:red],
		bar_width=ustrip(uconvert(lambda_unit, 100u"nm")),
		fillalpha=alpha,
		label="",
	)
end

function plot_stuff(T)
    ls3 = 10 .^ (range(-2, stop=4, length=1000))
    y = planck_spectrum(ls3.*1u"nm", T*1u"K")
    add_visible_light(u"nm", maximum(y), 0.7)
    plot!(
        ls3,
        #ls3,
        y,
        #xscale=:log10,
        #yscale=:log10,
        xlim=[100, 1500],
        xlabel="Wellenlänge [nm]",
        ylabel="Intensität [W/m³]",
        label="$T K",
        color=:black,
        grid=true,
        lw=3
    )
end

for T in [3000, 6000, 12000]
    pgfplotsx()
    pl = plot()
    plot_stuff(T)
    savefig(pl, "planck_$T.tex")

    gr()
    pl = plot()
    plot_stuff(T)
    savefig(pl, "planck_$T.png")

    pl = plot()
    plot_stuff(T)
    savefig(pl, "planck_$T.svg")
end
