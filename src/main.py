import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# import numpy as np
import os


def load_salary_data():
    """Load salary data from CSV files"""
    data = {}
    csv_path_2023 = os.path.join(os.path.dirname(__file__), "salary_2023.csv")
    csv_path_2024 = os.path.join(os.path.dirname(__file__), "salary_2024.csv")
    csv_path_2025 = os.path.join(os.path.dirname(__file__), "salary_2025.csv")

    if os.path.exists(csv_path_2023):
        data["2023"] = pd.read_csv(csv_path_2023)

    if os.path.exists(csv_path_2024):
        data["2024"] = pd.read_csv(csv_path_2024)

    if os.path.exists(csv_path_2025):
        data["2025"] = pd.read_csv(csv_path_2025)

    return data


def main():
    st.title("Salary Comparison Tool")
    st.write(
        "Compare actual vs. adjusted salaries with penetration rate analysis"
    )

    # Load salary data
    salary_data = load_salary_data()

    if not salary_data:
        st.error(
            "Salary data CSV files not found. Please check that the CSV files exist in the same directory as the script."
        )
        return

    # Sidebar for user inputs
    st.sidebar.header("Input Parameters")

    # Get available levels from 2024 data
    levels = salary_data["2024"]["Level"].unique().tolist()
    levels.sort()

    # Job level selection
    selected_level = st.sidebar.selectbox("Select Job Level", levels)

    # Get data for selected level
    level_data_2024 = salary_data["2024"][
        salary_data["2024"]["Level"] == selected_level
    ].iloc[0]
    level_data_2025 = salary_data["2025"][
        salary_data["2025"]["Level"] == selected_level
    ].iloc[0]

    # Years to analyze
    years = ["2023", "2024", "2025"]

    # Get data for selected level
    level_data_2023 = None
    if "2023" in salary_data:
        level_data_2023 = salary_data["2023"][
            salary_data["2023"]["Level"] == selected_level
        ].iloc[0]

    # Get actual salary input for each year
    actual_salaries = {}
    for year in years:
        default_value = 0
        if year == "2023" and level_data_2023 is not None:
            default_value = float(level_data_2023["Lower_Mid_Zone"])
        elif year == "2024":
            default_value = float(level_data_2024["Lower_Mid_Zone"])
        elif year == "2025":
            default_value = float(level_data_2025["Middle_Min"])

        actual_salaries[year] = st.sidebar.number_input(
            f"Your Actual Salary for {year} (DKK)",
            value=default_value,
            step=1000.0,
            key=f"actual_{year}",
        )

    # Create ranges data structure
    ranges = []

    # Add 2023 data if available
    if level_data_2023 is not None:
        ranges.append(
            {
                "year": "2023",
                "min": float(level_data_2023["Minimum"]),
                "max": float(level_data_2023["Maximum"]),
                "median": float(
                    (
                        level_data_2023["Lower_Mid_Zone"]
                        + level_data_2023["Upper_Mid_Zone"]
                    )
                    / 2
                ),
                "specific_price_1": actual_salaries["2023"],
            }
        )

    # Add 2024 data
    ranges.append(
        {
            "year": "2024",
            "min": float(level_data_2024["Minimum"]),
            "max": float(level_data_2024["Maximum"]),
            "median": float(
                (
                    level_data_2024["Lower_Mid_Zone"]
                    + level_data_2024["Upper_Mid_Zone"]
                )
                / 2
            ),
            "specific_price_1": actual_salaries["2024"],
        }
    )

    # Add 2025 data
    ranges.append(
        {
            "year": "2025",
            "min": float(level_data_2025["Lower_Min"]),
            "max": float(level_data_2025["Upper_Max"]),
            "median": float(
                (level_data_2025["Middle_Min"] + level_data_2025["Middle_Max"])
                / 2
            ),
            "specific_price_1": actual_salaries["2025"],
        }
    )

    # Select which year to base the penetration rate on
    base_year_index = (
        1 if len(ranges) > 2 else 0
    )  # Use 2024 (index 1) if we have 2023 data, otherwise use first year
    base_year = ranges[base_year_index]["year"]

    # Calculate relative position (penetration rate)
    relative_position = (
        ranges[base_year_index]["specific_price_1"]
        - ranges[base_year_index]["min"]
    ) / (ranges[base_year_index]["max"] - ranges[base_year_index]["min"])

    # Apply the same relative position to calculate adjusted salaries
    adjusted_salaries = []
    for range_data in ranges:
        adjusted = range_data["min"] + relative_position * (
            range_data["max"] - range_data["min"]
        )
        adjusted_salaries.append(adjusted)

    # Update the values dictionary to include the penetration rate in each bar
    values = ranges.copy()
    for val in values:
        val["penetration_rate"] = relative_position

    # Create a dataframe for comparison
    df_comparison = pd.DataFrame(
        {
            "Year": [val["year"] for val in values],
            "Min": [val["min"] for val in values],
            "Max": [val["max"] for val in values],
            "Median": [val["median"] for val in values],
            "Actual Salary": [val["specific_price_1"] for val in values],
            "Adjusted Salary": adjusted_salaries,
            f"Relative Position (Based on {base_year})": [relative_position]
            * len(values),
        }
    )

    # Display dataframe
    st.subheader("Salary Comparison Table")
    df_penetration = df_comparison.copy()
    df_penetration["Penetration Rate"] = df_penetration[
        f"Relative Position (Based on {base_year})"
    ].apply(lambda x: f"{x:.2%}")
    st.dataframe(df_penetration)

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define offsets for actual and adjusted salaries to avoid overlap
    actual_offset = -0.1  # Offset for actual salary (blue)
    adjusted_offset = 0.1  # Offset for adjusted salary (green)

    for index, val in enumerate(values):
        # Plot range bar
        ax.barh(
            index,
            val["max"] - val["min"],
            left=val["min"],
            height=0.4,
            color="grey",
            alpha=0.5,
            label="Range" if index == 0 else "",
        )

        # Plot median
        ax.axvline(
            x=val["median"],
            ymin=index / len(values) + 0.05,
            ymax=(index + 1) / len(values) - 0.05,
            color="red",
            linewidth=2,
            label="Median" if index == 0 else "",
        )

        # Plot actual salary (Blue X) with vertical offset
        ax.scatter(
            val["specific_price_1"],
            index + actual_offset,  # Apply vertical offset
            color="blue",
            marker="X",  # Use X marker
            s=100,  # Larger marker size
            zorder=5,
            label="Actual Salary (Blue X)" if index == 0 else "",
        )
        # Add text label for actual salary
        ax.text(
            val["specific_price_1"],
            index + actual_offset,
            f" {val['specific_price_1']:.0f} DKK",
            va="center",
            ha="left",
            color="blue",
            fontsize=9,
        )

        # Plot adjusted salary based on penetration rate (Green X) with vertical offset
        ax.scatter(
            adjusted_salaries[index],
            index + adjusted_offset,  # Apply vertical offset
            color="green",
            marker="X",  # Use X marker
            s=100,  # Larger marker size
            zorder=5,
            label="Adjusted Salary (Green X)" if index == 0 else "",
        )
        # Add text label for adjusted salary
        ax.text(
            adjusted_salaries[index],
            index + adjusted_offset,
            f" {adjusted_salaries[index]:.0f} DKK",
            va="center",
            ha="left",
            color="green",
            fontsize=9,
        )

        # Display penetration rate inside the bar
        penetration_text = f"Penetration Rate: {val['penetration_rate']:.2%}"
        ax.text(
            val["min"] + (val["max"] - val["min"]) / 2,
            index,
            penetration_text,
            va="center",
            ha="center",
            color="black",
            fontsize=10,
            fontweight="bold",
        )

    # Set labels
    ax.set_yticks(range(len(values)))
    ax.set_yticklabels([val["year"] for val in values])
    ax.set_xlabel("Salary (DKK)")
    ax.set_title(f"Level {selected_level} - Salary Range Comparison")
    ax.legend()
    plt.grid(axis="x", linestyle="--", alpha=0.7)

    # Format x-axis with thousand separators
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))
    )

    # Display plot in Streamlit
    st.subheader("Salary Visualization")
    st.pyplot(fig)

    # Explanation section
    st.markdown(
        f"""
    ### How to interpret:
    - **Grey bars**: Salary range for each year (Level {selected_level})
    - **Red lines**: Median salary for each year
    - **Blue X**: Your actual salary
    - **Green X**: Adjusted salary based on {base_year} penetration rate ({relative_position:.2%})
    - **Penetration Rate**: Your position within the salary range
    
    ### What does this mean?
    If your {base_year} salary maintains the same relative position ({relative_position:.2%}) 
    within the salary ranges for other years, your adjusted salaries would be:
    """
    )

    # Create a simple table of adjusted salaries for all years
    adjusted_df = pd.DataFrame(
        {
            "Year": [val["year"] for val in values],
            "Adjusted Salary (DKK)": [
                f"{adj:.0f}" for adj in adjusted_salaries
            ],
        }
    )
    st.table(adjusted_df)

    # Create a future trend projection
    st.subheader("Future Salary Trend Projection")
    st.write(
        "Projection of salary ranges for the next two years if current trends continue"
    )

    # Calculate average growth rates based on available data
    all_years = [int(val["year"]) for val in values]
    min_vals = [val["min"] for val in values]
    max_vals = [val["max"] for val in values]
    median_vals = [val["median"] for val in values]
    actual_vals = [val["specific_price_1"] for val in values]

    # Only proceed if we have at least 2 years of data to calculate growth
    if len(all_years) >= 2:
        # Calculate average yearly growth rates
        min_growth_rate = (min_vals[-1] / min_vals[0]) ** (
            1 / (len(all_years) - 1)
        ) - 1
        max_growth_rate = (max_vals[-1] / max_vals[0]) ** (
            1 / (len(all_years) - 1)
        ) - 1
        median_growth_rate = (median_vals[-1] / median_vals[0]) ** (
            1 / (len(all_years) - 1)
        ) - 1

        # Calculate penetration rates over time
        penetration_rates = []
        for i in range(len(all_years)):
            pen_rate = (actual_vals[i] - min_vals[i]) / (
                max_vals[i] - min_vals[i]
            )
            penetration_rates.append(pen_rate)

        # Project future years (2 years ahead)
        future_years = [max(all_years) + 1, max(all_years) + 2]
        all_years_with_future = all_years + future_years

        # Project future values
        projected_min = [
            min_vals[-1] * (1 + min_growth_rate) ** (i + 1) for i in range(2)
        ]
        projected_max = [
            max_vals[-1] * (1 + max_growth_rate) ** (i + 1) for i in range(2)
        ]
        projected_median = [
            median_vals[-1] * (1 + median_growth_rate) ** (i + 1)
            for i in range(2)
        ]

        # Calculate adjusted salaries for future years
        projected_adjusted = [
            min_val + relative_position * (max_val - min_val)
            for min_val, max_val in zip(projected_min, projected_max)
        ]

        # Combine historical and projected data
        all_min = min_vals + projected_min
        all_max = max_vals + projected_max
        all_median = median_vals + projected_median

        # Extend adjusted salaries with projections
        all_adjusted = adjusted_salaries + projected_adjusted

        # Create a trend visualization showing both the base trend and expected earnings
        fig2, ax2 = plt.subplots(figsize=(10, 6))

        # Combine historical and projected years
        combined_years = all_years + future_years

        # Show the min/max/median ranges as shaded areas
        ax2.fill_between(
            combined_years,
            all_min,
            all_max,
            alpha=0.2,
            color="gray",
            label="Salary Range",
        )

        # Plot the median line to show base trend
        ax2.plot(
            combined_years,
            all_median,
            "k--",
            linewidth=1.5,
            label="Median Trend",
        )

        # Plot actual historical salaries (only for years we have data)
        ax2.plot(
            all_years,
            actual_vals,
            "bo-",
            linewidth=2,
            markersize=8,
            label="Your Actual Salary",
        )

        # Plot expected salaries (including projections)
        ax2.plot(
            combined_years,
            all_adjusted,
            "go-",
            linewidth=2,
            markersize=8,
            label=f"Expected Salary ({relative_position:.2%} penetration)",
        )

        # Add vertical line to separate historical from projected data
        ax2.axvline(x=max(all_years), color="black", linestyle="--", alpha=0.7)
        ax2.text(
            max(all_years),
            min(all_min) * 0.98,
            "Historical | Projected",
            horizontalalignment="center",
            verticalalignment="bottom",
            bbox=dict(facecolor="white", alpha=0.8),
        )

        # Add data labels for expected salary points
        for i, (year, adjusted) in enumerate(
            zip(combined_years, all_adjusted)
        ):
            is_projected = i >= len(all_years)
            if is_projected:
                # Add labels for projected points
                ax2.annotate(
                    f"{adjusted:,.0f}",
                    (year, adjusted),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=10,
                    color="green",
                    weight="bold",
                    bbox=dict(facecolor="white", alpha=0.7),
                )

        # Format axes
        ax2.set_xticks(combined_years)
        ax2.set_xticklabels([str(year) for year in combined_years])
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Salary (DKK)")
        ax2.set_title(f"Level {selected_level} - Expected Salary Projection")

        # Format y-axis with thousand separators
        ax2.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, loc: "{:,.0f}".format(x))
        )

        # Add grid and legend
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc="upper left")

        # Show plot
        st.pyplot(fig2)

        # Add explanation of projected values
        st.markdown(
            f"""
        ### Expected Future Salary
        Based on the growth trends from {min(all_years)} to {max(all_years)}, here's what you can expect to earn in the coming years:
        """
        )

        # Create a simplified dataframe focusing on projected earnings
        future_df = pd.DataFrame(
            {
                "Year": future_years,
                "Expected Salary": [
                    f"{val:,.0f} DKK" for val in projected_adjusted
                ],
                "Growth from {max(all_years)}": [
                    f"{(val/adjusted_salaries[-1] - 1):.2%}"
                    for val in projected_adjusted
                ],
            }
        )

        st.table(future_df)

        # Create a more detailed table showing the full data
        st.markdown("### Detailed Projection Data")
        all_penetration = penetration_rates + [relative_position] * len(
            future_years
        )

        projection_df = pd.DataFrame(
            {
                "Year": all_years_with_future,
                "Minimum": [f"{val:,.0f}" for val in all_min],
                "Maximum": [f"{val:,.0f}" for val in all_max],
                "Penetration Rate": [f"{val:.2%}" for val in all_penetration],
                "Your Salary": [
                    f"{val:,.0f}" if i < len(actual_vals) else "TBD"
                    for i, val in enumerate(
                        actual_vals + ([0] * len(future_years))
                    )
                ],
                "Expected Salary": [f"{val:,.0f}" for val in all_adjusted],
            }
        )

        # Highlight the projected years
        def highlight_projected(row):
            if int(row.name) >= len(all_years):
                return ["background-color: rgba(144, 238, 144, 0.2)"] * len(
                    row
                )
            else:
                return [""] * len(row)

        st.dataframe(projection_df.style.apply(highlight_projected, axis=1))

        st.markdown(
            f"""
        ### How This Projection Works
        - Your {base_year} penetration rate is {relative_position:.2%}
        - The projection assumes you maintain this same position within future salary ranges
        - Salary ranges are projected to grow at {max_growth_rate:.2%} per year (based on historical data)
        - Your expected salary grows with the overall market for your level
        
        This projection gives you a realistic view of future earnings if market trends continue and you maintain the same relative position within your salary band.
        """
        )
    else:
        st.warning(
            "Need at least two years of historical data to project trends."
        )


if __name__ == "__main__":
    main()
