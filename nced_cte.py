import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from openpyxl import load_workbook

# Set the page layout and initial sidebar state
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Initializes current page in session state if it does not exist
if "current_page" not in st.session_state:
    st.session_state.current_page = "summary"

# Initialize filter selections in session state
if "selected_x_var" not in st.session_state:
    st.session_state.selected_x_var = None
if "selected_y_var" not in st.session_state:
    st.session_state.selected_y_var = None


def switch_page(page: str):
    st.session_state.current_page = page


# Sidebar Navigation
st.sidebar.subheader("Navigation")

home_button = st.sidebar.button(
    "🎯Home".upper(), on_click=switch_page, args=["home"]
)

cte_analysis_button = st.sidebar.button(
    "📈CTE Analysis".upper(), on_click=switch_page, args=["cte_analysis"]
)


# Home Page
def home():
    st.title("NCED: CTE Data Application📚")
    st.write("""
        This app explores county-level data on student enrollment in North Carolina's Education System (NCED), with a focus on Career and Technical Education (CTE) programs. 
        It provides insights into the diversity of career clusters across counties and tracks employment projections from 2021 to 2030.
        
        Key features include:
        - **Scatter Plot of CTE Data**: Interactive plot that enables the user to select the x and y axis to see distinct trends within CTE data. 
        (E.g., visualize the comparison of students enrolled to those enrolled in CTE courses or concentrating in CTE pathway)
        - **Unique Career Cluster Totals by County**: Visualizations highlighting the diversity in career clusters across counties, focusing on the overall trends and bottom 10 counties for career cluster participation.
        - **Employment Projections (2021 vs. 2030)**: A comparison of projected employment figures across various industries, offering a glimpse into future workforce trends.

        Dive into the data to explore how CTE programs are shaping future career opportunities at the county level.  
        """)
    st.write("More info on CTE programs can be found here:")    
    st.write("https://www.dpi.nc.gov/districts-schools/classroom-resources/career-and-technical-education")


# CTE Analysis Page
def cte_analysis():
    st.title("CTE Data Analysis📈")

    # Data dictionary for renaming columns
    data_dict = {
        'year': "Year",
        'agency_prefix': "Agency Prefix",
        'stu_enroll': "Student Enrollment",
        'cte_enroll': "CTE Course Enrollment",
        'county': "County",
        'district_code': "District Code",
        'sum_cluster_in_county': "Sum of Career Clusters in County",
        'sum_cluster_in_state': "Sum of Career Clusters in State",
        'unique_career_clusters_y': "Unique Career Clusters in County",
        'total_concentrators': "Total Concentrators in CTE Pathway"
    }
    
    # Display data dictionary
    # st.subheader("CTE Data Dictionary")
    # st.write(data_dict)
    
    # Load the dataset
    try:
        cte_df = pd.read_csv('data/ACTUAL_FINAL.csv')
        #  cte_df = pd.read_csv('ACTUAL_FINAL.csv')
    except Exception as e:
        st.error(f"Error loading CTE enrollment data: {e}")
        return
    
    # Rename columns in the dataset using the data dictionary
    cte_df.rename(columns=data_dict, inplace=True)
    
    # Features for scatterplot
    features = cte_df.select_dtypes(include=["number"]).columns.tolist()
    features = [col for col in features if col != "Year"]
    
    # Scatterplot variables
    selected_x_var = st.selectbox("Select the X-axis variable for Scatterplot:", features, index=0)
    selected_y_var = st.selectbox("Select the Y-axis variable for Scatterplot:", features, index=0)
    
    # Scatterplot and data table
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Scatterplot")
        scatter_chart = (
            alt.Chart(cte_df, title="Scatterplot of CTE Data")
            .mark_circle()
            .encode(
                x=alt.X(selected_x_var, scale=alt.Scale(zero=False)),
                y=alt.Y(selected_y_var, scale=alt.Scale(zero=False)),
                color=alt.Color(selected_y_var, scale=alt.Scale(scheme='viridis')),
                tooltip=["County", selected_x_var, selected_y_var],
            )
            .interactive()
        )
        st.altair_chart(scatter_chart, use_container_width=True)
    
    with col2:
        st.subheader("Data Table")
        st.dataframe(cte_df)
    
    # Unique Career Cluster Totals by County
    st.subheader("Unique Career Cluster Totals by County")
    if 'Unique Career Clusters in County' in cte_df.columns:
        county_totals = cte_df.groupby('County')['Unique Career Clusters in County'].sum().reset_index()
        county_totals_sorted = county_totals.sort_values(by='Unique Career Clusters in County', ascending=False)
        bottom_10_counties = county_totals_sorted.tail(10)
        
        col1, col2 = st.columns(2)
        with col1:
            all_counties_bar_chart = px.bar(
                county_totals_sorted,
                x='Unique Career Clusters in County',
                y='County',
                title="Unique Career Cluster Totals by County",
                labels={'County': 'County', 'Unique Career Clusters in County': 'Diversity Total'},
                color='Unique Career Clusters in County',
                color_continuous_scale='YlOrRd'
            )
            st.plotly_chart(all_counties_bar_chart, use_container_width=True)
        
        with col2:
            bottom_10_bar_chart = px.bar(
                bottom_10_counties,
                x='Unique Career Clusters in County',
                y='County',
                title="Bottom 10 Counties of Focus (Unique Career Cluster Totals)",
                labels={'County': 'County', 'Unique Career Clusters in County': 'Diversity Total'},
                color='Unique Career Clusters in County',
                color_continuous_scale='YlOrRd'
            )
            st.plotly_chart(bottom_10_bar_chart, use_container_width=True)
    else:
        st.warning("'Unique Career Clusters in County' column not found in the dataset.")
    
    # Employment Projections
    st.subheader("Employment Projections (2021 vs 2030)")

    try:
        # projections_df = pd.read_excel(
        #     r"C:\Users\dylan\DSBA 5122\NCED CTE Final\Employment Projections - 2-digit (Super-industry).xlsx",
        #     engine="openpyxl"
        # )
         projections_df = pd.read_excel(
            r"data/Employment Projections - 2-digit (Super-industry).xlsx",
            engine="openpyxl"
        )
    except Exception as e:
        st.error(f"Error loading employment projections data: {e}")
        return

    if not projections_df.empty:
        # Filter and plot projections data
        industry_titles = projections_df["Industry Title"].unique().tolist()
        industry_title = st.selectbox("Select Industry Title:", industry_titles)

        # Filter projections by industry title
        filtered_df = projections_df[projections_df["Industry Title"] == industry_title]

        # Drop rows with missing projections for 2021 or 2030
        filtered_df = filtered_df.dropna(subset=[2021, 2030])

        # Output the filtered dataframe to inspect
        st.write(f"Filtered DataFrame for Industry: {industry_title}")
        st.dataframe(filtered_df)  # Shows the table of filtered data

        # Plot the projections
        bar_chart = px.bar(
            filtered_df,
            x="Industry Title",
            y=[2021, 2030],
            title=f"Employment Projections for {industry_title} (2021 vs 2030)",
            barmode="group",
            labels={"value": "Projections", "variable": "Year"},
        )
        bar_chart.update_layout(
            xaxis_title="Industry Title",
            yaxis_title="Employment Projections",
            legend_title="Year",
            width=800,
            height=500,
        )
        st.plotly_chart(bar_chart, use_container_width=True)
    else:
        st.warning("No data found for employment projections.")


# Page routing
fn_map = {
    "home": home,
    "cte_analysis": cte_analysis,
}

# Render the page based on the current state
main_workflow = fn_map.get(st.session_state.current_page, home)
main_workflow()
