import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt
import yaml
import os
import glob
import re
from datetime import datetime


def parse_markdown_with_yaml(file_path):
    """Parse a markdown file with YAML front matter."""
    with open(file_path, "r") as file:
        content = file.read()

    # Extract YAML front matter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            markdown_content = parts[2].strip()
            try:
                metadata = yaml.safe_load(yaml_content)
                return {"metadata": metadata, "content": markdown_content}
            except yaml.YAMLError as e:
                st.error(f"Error parsing YAML in {file_path}: {e}")
                return None

    # No valid YAML front matter found
    return {"metadata": {}, "content": content}


def get_all_achievements(directory):
    """Get all achievement files from the specified directory."""
    # Get all markdown files
    files = glob.glob(os.path.join(directory, "*.md"))
    achievements = []

    for file in files:
        # Skip non-achievement files
        if os.path.basename(file) in ["CLAUDE.md", "plan.md"]:
            continue

        parsed = parse_markdown_with_yaml(file)
        if parsed:
            # Add filename to the metadata
            filename = os.path.basename(file)
            parsed["filename"] = filename

            # Extract date from filename (YYYY-MM-DD-title.md)
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})-.*", filename)
            if date_match:
                parsed["file_date"] = date_match.group(1)
            else:
                # Try to get date from metadata
                parsed["file_date"] = parsed.get("metadata", {}).get(
                    "date", "Unknown"
                )

            achievements.append(parsed)

    # Sort by date (newest first)
    achievements.sort(key=lambda x: x.get("file_date", ""), reverse=True)
    return achievements


def load_summary_yaml(file_path):
    """Load the summary YAML file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                st.error(f"Error parsing summary YAML: {e}")
    return {}


def generate_achievement_metrics(achievements):
    """Generate metrics from achievements."""
    total = len(achievements)

    # Extract categories
    categories = {}
    for achievement in achievements:
        category = achievement.get("metadata", {}).get(
            "category", "Uncategorized"
        )
        categories[category] = categories.get(category, 0) + 1

    # Extract dates for trend analysis
    dates = {}
    for achievement in achievements:
        date_str = achievement.get("file_date", "")
        if date_str and date_str != "Unknown":
            # Extract year-month
            year_month = date_str[:7]  # YYYY-MM
            dates[year_month] = dates.get(year_month, 0) + 1

    # Sort dates
    sorted_dates = dict(sorted(dates.items()))

    # Find highest impact achievemen
    highest_impact = None
    highest_impact_metrics = []

    for achievement in achievements:
        metrics = achievement.get("metadata", {}).get("metrics", [])
        if metrics and (
            highest_impact is None
            or len(metrics) > len(highest_impact_metrics)
        ):
            highest_impact = achievement.get("metadata", {}).get(
                "title", "Unknown"
            )
            highest_impact_metrics = metrics

    return {
        "total_achievements": total,
        "categories": categories,
        "trend_over_time": sorted_dates,
        "highest_impact": highest_impact,
    }


def render_achievements_dashboard():
    """Render the achievements dashboard"""
    st.title("Professional Achievements Dashboard")
    st.write("Track and visualize your professional achievements and impact")

    # Define the achievements directory
    achievements_dir = os.path.join(os.path.dirname(__file__), "achievements")

    # Create achievements directory if it doesn't exis
    if not os.path.exists(achievements_dir):
        os.makedirs(achievements_dir)
        st.info(f"Created achievements directory at {achievements_dir}")

    # Check for summary.yaml
    summary_path = os.path.join(achievements_dir, "summary.yaml")
    summary_data = load_summary_yaml(summary_path)

    # Load all achievements
    achievements = get_all_achievements(achievements_dir)

    # If no achievements are found, show instructions
    if not achievements:
        st.warning(
            "No achievement files found. Create your first achievement!"
        )
        st.markdown(
            """
        ## How to Add Achievements

        1. Create a new markdown file in the `achievements` directory
        2. Follow naming convention: `YYYY-MM-DD-title.md`
        3. Include YAML front matter with metadata

        ### Example:
        ```markdown
        ---
        title: "Optimized API Performance"
        date: "2024-03-01"
        category: "Technical Impact"
        tags: ["performance", "latency", "backend"]
        metrics:
          - key: "Latency Reduction"
            value: "40%"
          - key: "Throughput Increase"
            value: "2x"
        impact:
          - "Decreased latency from 500ms to 300ms"
          - "Improved system throughput by 2x"
        summary: "By optimizing database queries, I significantly improved API
                  performance, reducing response time by 40% and increasing
                  throughput."
        ---

        # Optimizing API Performance

        One of my biggest wins this quarter was improving
        the API response time,
        which had been a major bottleneck. By optimizing database queries and
        implementing caching, I achieved:

        - 40% lower latency
        - 2x increase in throughpu

        This improvement led to faster end-user interactions and a smoother
        experience for our customers.
        ```
        """
        )
        return

    # Generate metrics if summary.yaml doesn't exist or needs updating
    metrics = generate_achievement_metrics(achievements)

    # Sidebar for filtering
    st.sidebar.header("Achievements Filters")

    # Extract all categories
    all_categories = list(metrics["categories"].keys())
    selected_categories = st.sidebar.multiselect(
        "Categories",
        all_categories,
        default=all_categories,
        key="achievement_categories",
    )

    # Extract all tags
    all_tags = set()
    for achievement in achievements:
        tags = achievement.get("metadata", {}).get("tags", [])
        for tag in tags:
            all_tags.add(tag)

    selected_tags = st.sidebar.multiselect(
        "Tags", list(all_tags), key="achievement_tags"
    )

    # Date range filter
    all_dates = [
        achievement.get("file_date", "")
        for achievement in achievements
        if achievement.get("file_date", "") != "Unknown"
    ]

    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)
        date_range = st.sidebar.date_input(
            "Date Range",
            [
                datetime.strptime(min_date, "%Y-%m-%d").date(),
                datetime.strptime(max_date, "%Y-%m-%d").date(),
            ],
            key="achievement_dates",
        )

    # Filter achievements based on selections
    filtered_achievements = achievements.copy()

    # Filter by category
    if selected_categories:
        filtered_achievements = [
            a
            for a in filtered_achievements
            if a.get("metadata", {}).get("category", "Uncategorized")
            in selected_categories
        ]

    # Filter by tags
    if selected_tags:
        filtered_achievements = [
            a
            for a in filtered_achievements
            if any(
                tag in a.get("metadata", {}).get("tags", [])
                for tag in selected_tags
            )
        ]

    # Filter by date range
    if "date_range" in locals() and len(date_range) == 2:
        start_date = date_range[0]
        end_date = date_range[1]
        filtered_achievements = [
            a
            for a in filtered_achievements
            if a.get("file_date", "") != "Unknown"
            and start_date
            <= datetime.strptime(a.get("file_date", ""), "%Y-%m-%d").date()
            <= end_date
        ]

    # Display KPI Cards in a row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Achievements", metrics["total_achievements"])

    with col2:
        st.metric("Biggest Win", metrics["highest_impact"] or "None")

    with col3:
        # Find most common category
        if metrics["categories"]:
            top_category = max(
                metrics["categories"].items(), key=lambda x: x[1]
            )
            st.metric("Top Category", f"{top_category[0]} ({top_category[1]})")
        else:
            st.metric("Top Category", "None")

    # Visualizations section
    st.subheader("📊 Achievement Analytics")

    # Create tabs for different visualizations
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(
        ["Trend Over Time", "Category Breakdown", "Impact Leaderboard"]
    )

    with viz_tab1:
        # Trend over time visualization
        if metrics["trend_over_time"]:
            trend_df = pd.DataFrame(
                {
                    "Month": list(metrics["trend_over_time"].keys()),
                    "Count": list(metrics["trend_over_time"].values()),
                }
            )

            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.plot(
                trend_df["Month"], trend_df["Count"], marker="o", linewidth=2
            )
            ax1.set_title("Achievements Over Time")
            ax1.set_xlabel("Month")
            ax1.set_ylabel("Number of Achievements")
            ax1.grid(True, linestyle="--", alpha=0.7)

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig1)
        else:
            st.info("Not enough data to generate trend visualization")

    with viz_tab2:
        # Category breakdown visualization
        if metrics["categories"]:
            categories_df = pd.DataFrame(
                {
                    "Category": list(metrics["categories"].keys()),
                    "Count": list(metrics["categories"].values()),
                }
            )

            fig2, ax2 = plt.subplots(figsize=(8, 8))
            ax2.pie(
                categories_df["Count"],
                labels=categories_df["Category"],
                autopct="%1.1f%%",
                startangle=90,
                shadow=False,
            )
            ax2.axis("equal")  # Equal aspect ratio for circular pie char
            plt.title("Achievement Categories")
            plt.tight_layout()

            st.pyplot(fig2)
        else:
            st.info("No category data available")

    with viz_tab3:
        # Impact leaderboard visualization
        impact_data = []
        for achievement in achievements:
            title = achievement.get("metadata", {}).get("title", "Unknown")
            metrics_list = achievement.get("metadata", {}).get("metrics", [])

            # Calculate an impact score (simple implementation)
            impact_score = len(metrics_list)

            impact_data.append({"title": title, "impact_score": impact_score})

        if impact_data:
            impact_df = pd.DataFrame(impact_data)
            impact_df = impact_df.sort_values(
                "impact_score", ascending=False
            ).head(10)

            fig3, ax3 = plt.subplots(figsize=(10, 6))
            bars = ax3.barh(impact_df["title"], impact_df["impact_score"])
            ax3.set_title("Top Achievements by Impact")
            ax3.set_xlabel("Impact Score")

            # Add labels to the bars
            for bar in bars:
                width = bar.get_width()
                label_y_pos = bar.get_y() + bar.get_height() / 2
                ax3.text(
                    width + 0.1,
                    label_y_pos,
                    s=f"{width}",
                    ha="left",
                    va="center",
                )

            plt.tight_layout()
            st.pyplot(fig3)
        else:
            st.info("No impact data available")

    # Achievement Lis
    st.subheader("📝 Achievement List")

    if not filtered_achievements:
        st.warning("No achievements match the selected filters")
    else:
        for i, achievement in enumerate(filtered_achievements):
            title = achievement.get("metadata", {}).get("title", "Untitled")
            date = achievement.get("file_date", "Unknown")

            with st.expander(f"{date} - {title}"):
                # Display metadata in a clean forma
                category = achievement.get("metadata", {}).get(
                    "category", "Uncategorized"
                )
                st.markdown(f"**Category:** {category}")

                # Display tags
                tags = achievement.get("metadata", {}).get("tags", [])
                if tags:
                    tags_str = " ".join([f"`{tag}`" for tag in tags])
                    st.markdown(f"**Tags:** {tags_str}")

                # Display metrics
                metrics_list = achievement.get("metadata", {}).get(
                    "metrics", []
                )
                if metrics_list:
                    st.markdown("**Metrics:**")
                    for metric in metrics_list:
                        key = metric.get("key", "Unknown")
                        value = metric.get("value", "Unknown")
                        st.markdown(f"- {key}: **{value}**")

                # Display impac
                impact_list = achievement.get("metadata", {}).get("impact", [])
                if impact_list:
                    st.markdown("**Impact:**")
                    for impact in impact_list:
                        st.markdown(f"- {impact}")

                # Display summary
                summary = achievement.get("metadata", {}).get("summary", "")
                if summary:
                    st.markdown(f"**Summary:** {summary}")

                # Display the markdown conten
                st.markdown("---")
                st.markdown(achievement.get("content", ""))

    # AI-Generated Summary (simplified version)
    if filtered_achievements:
        st.subheader("📖 Achievement Summary")

        # Simple template-based approach (could use AI in real implementation)
        total = len(filtered_achievements)

        categories_str = "various areas"
        if selected_categories:
            categories_str = ", ".join(selected_categories[:3])

        # Get the date range for the summary
        date_range_str = ""
        if "date_range" in locals() and len(date_range) == 2:
            date_range_str = (
                f"from {date_range[0].strftime('%B %Y')} "
                f"to {date_range[1].strftime('%B %Y')}"
            )
        elif all_dates:
            earliest = datetime.strptime(min(all_dates), "%Y-%m-%d")
            latest = datetime.strptime(max(all_dates), "%Y-%m-%d")
            date_range_str = (
                f"from {earliest.strftime('%B %Y')} "
                f"to {latest.strftime('%B %Y')}"
            )

        # Find top achievemen
        top_achievement = None
        for achievement in filtered_achievements:
            metrics_list = achievement.get("metadata", {}).get("metrics", [])
            if metrics_list and (
                top_achievement is None
                or len(metrics_list)
                > len(top_achievement.get("metadata", {}).get("metrics", []))
            ):
                top_achievement = achievement

        top_impact = ""
        if top_achievement:
            # Try to get the first metric
            metrics_list = top_achievement.get("metadata", {}).get(
                "metrics", []
            )
            if metrics_list and len(metrics_list) > 0:
                first_metric = metrics_list[0]
                metric_key = first_metric.get("key", "improving performance")
                metric_val = first_metric.get("value", "a significant amount")
                top_impact = f", {metric_key} by {metric_val}"

        # Build the summary
        highest_impact = metrics.get("highest_impact") or "various projects"

        top_category_name = "your field"
        if "top_category" in locals() and top_category:
            top_category_name = top_category[0]

        summary = f"""
        Over {date_range_str}, you have recorded **{total} achievements**
        across {categories_str}. Your most impactful work was
        **{highest_impact}**{top_impact}. You've consistently demonstrated
        strong contributions, particularly in **{top_category_name}**.
        """

        st.markdown(summary)


if __name__ == "__main__":
    render_achievements_dashboard()
    render_achievements_dashboard()
