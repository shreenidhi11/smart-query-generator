import streamlit as st
import re

# --- 1. The "Brain": A Synonym Dictionary ---
SYNONYM_MAP = {
    "software engineer": ["Software Developer", "Backend Engineer", "Full Stack Developer", "Developer", "Programmer"],
    "python developer": ["Python Engineer", "Backend Engineer", "Software Engineer (Python)", "Data Engineer"],
    "python engineer": ["Python Developer", "Backend Engineer", "Software Engineer (Python)", "Data Engineer"],
    "data scientist": ["Data Analyst", "Machine Learning Engineer", "ML Engineer", "Business Intelligence Analyst"],
    "data engineer": ["Data Architect", "Pipeline Developer", "ETL Developer", "Big Data Engineer"],
    "frontend developer": ["Frontend Engineer", "UI Developer", "React Developer", "Web Developer"],
    "backend developer": ["Backend Engineer", "Software Engineer", "Python Developer", "Java Developer"],
    "full stack developer": ["Full Stack Engineer", "Software Engineer", "Web Developer"],
    "machine learning engineer": ["ML Engineer", "Data Scientist", "AI Engineer", "Computer Vision Engineer"],
    "devops engineer": ["SRE", "Site Reliability Engineer", "Platform Engineer", "Cloud Engineer"],
    "product manager": ["PM", "Technical Product Manager", "Product Owner"]
}

# --- 2. The Query "Ingredients" ---
ACTION_PHRASES = [
    "hiring",
    "we're hiring",
    "is hiring",
    "recruiting",
    "join our team",
    "looking for"
]

EXCLUSION_PHRASES = [
    "intern",
    "internship",
    "course",
    "bootcamp",
    "trainee",
    "senior",
    "sr."
]


# --- 3. The Function to Get Synonyms ---
def get_synonyms(job_title):
    """
    Finds synonyms from the pre-defined map.
    """
    key = job_title.lower().strip()  # Clean the input

    # Check for a direct match
    if key in SYNONYM_MAP:
        return SYNONYM_MAP[key]

    # Check for partial matches
    for map_key, synonyms in SYNONYM_MAP.items():
        if map_key in key:
            return synonyms

    return []  # Return empty list if no match


# --- 4. NEW: The Multi-Query Builder ---
def build_boolean_queries(main_title, synonyms):
    """
    Builds a *list* of queries, from broad to narrow.
    """

    # --- 4a. Build the reusable "parts" ---
    all_titles = [main_title] + synonyms
    titles_query_part = " OR ".join([f'"{t.title()}"' for t in all_titles])
    titles_query_part = f"({titles_query_part})"  # e.g., ("Software Engineer" OR "Developer")

    main_title_part = f'"{main_title.title()}"'  # e.g., "Software Engineer"

    action_query_part = " OR ".join([f'"{p}"' for p in ACTION_PHRASES])
    action_query_part = f"({action_query_part})"  # e.g., ("hiring" OR "recruiting")

    exclusion_query_part = " OR ".join([f'"{p}"' for p in EXCLUSION_PHRASES])
    exclusion_query_part = f"NOT ({exclusion_query_part})"  # e.g., NOT ("intern" OR "senior")

    # --- 4b. Assemble the list of 6 queries ---
    queries = []

    # Query 1: Broad & On-Target (Titles AND Actions)
    # This is often the most effective one.
    queries.append(f"{titles_query_part} AND {action_query_part}")

    # Query 2: The "Perfect" Query (Full)
    # This is the one that was failing, but it's good to have.
    # queries.append(f"{titles_query_part} AND {action_query_part} AND {exclusion_query_part}")
    queries.append(f"{titles_query_part} AND {action_query_part}")

    # Query 3: Focused Search (Main Title + Actions + Exclusions)
    # Good if the synonyms are making it too broad.
    # queries.append(f"{main_title_part} AND {action_query_part} AND {exclusion_query_part}")

    # Query 4: Simple Broad Search (All Titles + "hiring")
    # A much simpler query for LinkedIn to parse.
    queries.append(f'{titles_query_part} AND "hiring"')

    # Query 5: Simple Focused Search (Main Title + "hiring")
    # The simplest, most direct search.
    queries.append(f'{main_title_part} AND "hiring"')

    # Query 6: Just Titles
    # Lets you manually scan all posts for these roles.
    queries.append(titles_query_part)

    return queries


# --- 5. The Streamlit UI (Updated) ---
st.set_page_config(layout="wide")
st.title("🚀 Smart Job Query Generator (v4)")
st.markdown("Enter a job title. I'll generate **6 variations** of LinkedIn **Posts** search queries for you.")
st.info(
    "ℹ️ **Tip:** Your last query was too long! Try these queries one by one, starting with #1. Remember to filter by **'Posts'**!")

job_title = st.text_input("Enter your desired job title:", "Software Engineer")

if st.button("Generate Queries"):  # Renamed button
    if not job_title:
        st.error("Please enter a job title.")
    else:
        with st.spinner("Building your query list..."):

            # 1. Get synonyms from our reliable dictionary
            synonyms = get_synonyms(job_title)

            if synonyms:
                st.subheader("Found these related roles:")
                st.write(", ".join(synonyms))
            else:
                st.warning(f"No pre-defined synonyms found. Building queries with the main title only.")

            # 2. Build the *list* of queries
            st.subheader("Here is your query list:")
            st.markdown("Start with Query 1. If you get no results, try Query 2, and so on.")

            queries_list = build_boolean_queries(job_title, synonyms)

            # 3. Display each query
            for i, query in enumerate(queries_list, 1):
                st.markdown(f"---")  # Horizontal line
                st.markdown(f"**Query {i}:**")
                st.code(query, language="text")

                # We need a unique key for each button
                st.button("Copy", key=f"copy_{i}", on_click=lambda s=query: st.toast(f"Copied Query {i}!"), args=())