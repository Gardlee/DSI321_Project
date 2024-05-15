import streamlit as st
import pandas as pd
import sqlalchemy
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image

# Connection string to the PostgreSQL database
DATABASE_URL = "postgresql+psycopg2://user:password@postgres:5432/datascience"
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/datascience"

# Setup database connection
@st.cache_resource
def get_database_connection():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    return engine.connect()

# Fetch dataset names from the database
@st.cache_data
def get_datasets(_conn):
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    return pd.read_sql(query, _conn)

# Fetch metadata for a specific table
@st.cache_data
def get_table_description(_conn, table_name):
    query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
    return pd.read_sql(query, _conn)

# Load data from a specific table
@st.cache_data
def load_data(_conn, table_name):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, _conn)

st.set_page_config(page_title='DSI_OMD_TU', layout='wide',
                   initial_sidebar_state=st.session_state.get('sidebar_state', 'collapsed'),
)
#st.image("dsiomdtu.png", use_column_width=True)

#st.snow()

def main():
    st.sidebar.image("dsiomdtu.png", use_column_width=True , width=250)
    st.title("DSI_OMD_TU Dataset Explorer")

    conn = get_database_connection()
    datasets = get_datasets(conn)
    dataset_names = datasets['table_name'].tolist()

    if not dataset_names:
        st.error("No datasets found in the database.")
        return

    dataset_selected = st.sidebar.selectbox("Select a dataset", dataset_names)

    if dataset_selected:
        # Display metadata
        metadata = get_table_description(conn, dataset_selected)
        if not metadata.empty:
            st.write(f"Metadata for {dataset_selected}:")
            st.dataframe(metadata)
        else:
            st.write("No metadata available.")

        # Load and display data
        data = load_data(conn, dataset_selected)
        if not data.empty:
            st.write("Data Preview:")
            st.dataframe(data.head())

            # Basic EDA options
            if st.button("Show Info"):
                buffer = StringIO()
                data.info(buf=buffer)
                s = buffer.getvalue()
                st.text(s)

            if st.button("Show Distribution"):
                st.write(data.describe())

            # Add Dropdown for different types of plots
            plot_type = st.selectbox("Select plot type", ["Histogram", "Pie Chart", "Line Chart", "Bar Chart"])
            # Add Histogram option
            if plot_type == "Histogram":
                columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if columns:
                    column_selected = st.selectbox("Select column for histogram", columns)
                    if st.button("Show Histogram"):
                        fig, ax = plt.subplots()
                        sns.histplot(data[column_selected], kde=True, ax=ax)
                        st.pyplot(fig)
                else:
                    st.write("No numerical columns available for histogram.")
            # Add Pie Chart option
            elif plot_type == "Pie Chart":
                categorical_columns = data.select_dtypes(include=['object', 'category']).columns.tolist()
                if categorical_columns:
                    pie_column_selected = st.selectbox("Select column for pie chart", categorical_columns)
                    if st.button("Show Pie Chart"):
                        pie_data = data[pie_column_selected].value_counts().reset_index()
                        pie_data.columns = [pie_column_selected, 'count']
                        fig = px.pie(pie_data, names=pie_column_selected, values='count', title=f"Pie chart of {pie_column_selected}")
                        st.plotly_chart(fig)
                else:
                    st.write("No categorical columns available for pie chart.")
            # Add Line Chart option
            elif plot_type == "Line Chart":
                numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if numerical_columns:
                    x_column = st.selectbox("Select X-axis column", numerical_columns)
                    y_column = st.selectbox("Select Y-axis column", numerical_columns)
                    if st.button("Show Line Chart"):
                        fig = px.line(data, x=x_column, y=y_column, title="Line Chart")
                        st.plotly_chart(fig)
                else:
                    st.write("No numerical columns available for line chart.")
            # Add Bar Chart option
            elif plot_type == "Bar Chart":
                numerical_columns = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if numerical_columns:
                    x_column = st.selectbox("Select X-axis column", numerical_columns)
                    y_column = st.selectbox("Select Y-axis column", numerical_columns)
                    if st.button("Show Bar Chart"):
                        fig = px.bar(data, x=x_column, y=y_column, title="Bar Chart")
                        st.plotly_chart(fig)
                else:
                    st.write("No numerical columns available for bar chart.")

        else:
            st.write("No data available for this dataset.")

if __name__ == "__main__":
    main()
