from scipy.interpolate import make_interp_spline
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


def create_other_plots(biometria, value, week):
    percentiles_data = {
        "Circunferência Craniana (HC)": np.array([79, 126, 177, 222, 262, 293, 317, 337]),
        "Circunferência Abdominal (AC)": np.array([62, 103, 153, 201, 240, 275, 301, 327]),
        "Comprimento do Fêmur (FL)": np.array([11, 21, 31, 40, 49, 57, 63, 69]),
        "Diâmetro Biparietal (BPD)": np.array([21, 35, 49, 62, 72, 82, 89, 95]),
        "Peso Fetal Estimado (EFW)": np.array([50, 150, 400, 800, 1300, 1800, 2300, 2800])
    }

    reference_weeks = np.array([12, 16, 20, 24, 28, 32, 36, 40])
    percentile_50 = percentiles_data[biometria]

    # Set global font size
    plt.rcParams['font.size'] = 8  # Adjust this value as needed

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(11.69, 8.27), facecolor="#1a1a2e", dpi=300)  # A4 size in inches
    ax.set_facecolor("#1a1a2e")

    # Calculate approximate standard deviations
    std_dev = percentile_50 * 0.1

    percentil_90 = percentile_50 + 1.28 * std_dev
    percentil_10 = percentile_50 - 1.28 * std_dev

    # Interpolate the data
    xnew = np.linspace(reference_weeks.min(), reference_weeks.max(), 1000)
    spl_10 = make_interp_spline(reference_weeks, percentil_10, k=3)
    spl_50 = make_interp_spline(reference_weeks, percentile_50, k=3)
    spl_90 = make_interp_spline(reference_weeks, percentil_90, k=3)

    percentil_10_smooth = spl_10(xnew)
    percentil_50_smooth = spl_50(xnew)
    percentil_90_smooth = spl_90(xnew)

    ax.set_yscale("linear")

    # Plot interpolated lines
    ax.plot(xnew, percentil_10_smooth, label="Percentil 10", color="cyan")
    ax.plot(xnew, percentil_50_smooth, label="Percentil 50", color="white")
    ax.plot(xnew, percentil_90_smooth, label="Percentil 90", color="magenta")

    # Fill between percentiles
    ax.fill_between(
        xnew,
        percentil_10_smooth,
        percentil_90_smooth,
        color="lime",
        alpha=0.1,
        label="10%-90% Range",
    )

    # Plot current measurement
    ax.scatter(
        week,
        value,
        color="yellow",
        edgecolor="white",
        s=150,
        zorder=5,
        label="Current Measurement",
    )

    # Customize the plot
    ax.set_xlabel("Semanas de Gestacao", fontsize=14, fontweight="bold", color="white", labelpad=12)
    ax.set_ylabel(f"{biometria} (mm)", fontsize=14, fontweight="bold", color="white", labelpad=12)
    ax.set_title(f"{biometria} por Semana de Gestacao", fontsize=14, fontweight="bold", color="white", pad=20)

    # Customize ticks
    ax.tick_params(axis='both', which='major', labelsize=8, colors="white")

    # Customize legend
    legend = ax.legend(loc="upper left", fontsize=8, frameon=True, facecolor="#1a1a2e", edgecolor="white")
    for text in legend.get_texts():
        text.set_color("white")

    # Add the measurement point annotation
    ax.annotate(f'{value:.2f}', (week, value), xytext=(5, 5),
                textcoords='offset points', ha='left', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                fontsize=8)

    # Add a grid
    ax.grid(True, linestyle="--", alpha=0.3, color="#ffffff")

    # Customize spines
    for spine in ax.spines.values():
        spine.set_color("white")
        spine.set_linewidth(1)

    plt.tight_layout()
    plt.savefig(f"{biometria}.png")
    plt.close(fig)
