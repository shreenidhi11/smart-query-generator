import streamlit as st
import re
from transformers import pipeline


# --- 1. Load the LLM (This will be cached) ---
@st.cache_resource
def load_model():
    """Loads the T5 model one time and caches it."""
    # st.toast("Loading AI model... (this may take a moment on first run)")
    return pipeline("text2text-generation", model="google/flan-t5-base")


# --- 2. The Query "Ingredients" (from v4) ---
ACTION_PHRASES = [
    "hiring",
    "we're hiring",
    "is hiring",
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


# --- 3. NEW: The LLM-Powered Synonym Generator ---
def get_synonyms_from_llm(job_title, generator):
    """
    Uses the LLM to generate synonyms and aggressively cleans the output.
    """

    # This prompt is a direct command, which works better.
    # We ask for "comma-separated" to guide the format.
    prompt = f"""
    Task: Generate a list of 4 common synonyms or related job titles for "{job_title}".
    Format: A single line, comma-separated.
    Titles:
    """

    try:
        outputs = generator(prompt, max_length=128, num_return_sequences=1)
        raw_text = outputs[0]['generated_text']

        # --- Robust Parsing Logic ---
        # The LLM output is messy. We clean it.
        synonyms = []

        # Split by comma OR a newline
        candidates = re.split(r'[,\n]', raw_text)

        for s in candidates:
            synonym = s.strip().title()  # Clean, strip whitespace, capitalize

            # Filter out junk:
            if not synonym:
                continue  # Skip empty strings
            if len(synonym) > 35:
                continue  # Skip any random sentences it generated
            if synonym.lower() == job_title.lower():
                continue  # Skip if it just repeats the input

            synonyms.append(synonym)

        return list(set(synonyms))  # Return unique, clean synonyms

    except Exception as e:
        st.error(f"Error calling LLM: {e}")
        return []


# --- 4. The Reliable Multi-Query Builder (from v4) ---
def build_boolean_queries(main_title, synonyms):
    """
    Builds a *list* of queries, from broad to narrow.
    (This is identical to v4)
    """

    # Build the reusable "parts"
    all_titles = [main_title] + synonyms
    titles_query_part = " OR ".join([f'"{t.title()}"' for t in all_titles])
    titles_query_part = f"({titles_query_part})"

    main_title_part = f'"{main_title.title()}"'

    action_query_part = " OR ".join([f'"{p}"' for p in ACTION_PHRASES])
    action_query_part = f"({action_query_part})"

    exclusion_query_part = " OR ".join([f'"{p}"' for p in EXCLUSION_PHRASES])
    exclusion_query_part = f"NOT ({exclusion_query_part})"

    # Assemble the list of 6 queries
    queries = []
    queries.append(f"{titles_query_part} AND {action_query_part}")
    queries.append(f"{titles_query_part} AND {action_query_part} AND {exclusion_query_part}")
    queries.append(f"{main_title_part} AND {action_query_part} AND {exclusion_query_part}")
    queries.append(f'{titles_query_part} AND "hiring"')
    queries.append(f'{main_title_part} AND "hiring"')
    queries.append(titles_query_part)

    return queries


# --- 5. The Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🧠 Smart Job Query Generator (v5 - AI Hybrid)")
st.markdown("Enter a job title. I'll use an **LLM** to brainstorm synonyms and generate 6 query variations.")
st.info("ℹ️ **Tip:** Try these queries one by one in the LinkedIn **Posts** filter, starting with #1.")

# Load the model at the start
try:
    st.toast("Loading AI model... (this may take a moment on first run)")
    generator = load_model()

    job_title = st.text_input("Enter your desired job title:", "Software Engineer")

    if st.button("Generate Queries"):
        if not job_title:
            st.error("Please enter a job title.")
        else:
            with st.spinner("🧠 Asking AI for related roles..."):

                # 1. Get synonyms from the LLM
                synonyms = get_synonyms_from_llm(job_title, generator)

                if synonyms:
                    st.subheader("AI found these related roles:")
                    st.write(", ".join(synonyms))
                else:
                    st.warning(f"The AI didn't return usable synonyms. Building queries with the main title only.")

                # 2. Build the *list* of queries
                st.subheader("Here is your query list:")

                queries_list = build_boolean_queries(job_title, synonyms)

                # 3. Display each query
                for i, query in enumerate(queries_list, 1):
                    st.markdown(f"---")
                    st.markdown(f"**Query {i}:**")
                    st.code(query, language="text")
                    st.button("Copy", key=f"copy_{i}", on_click=lambda s=query: st.toast(f"Copied Query {i}!"), args=())

except Exception as e:
    st.error(f"A critical error occurred: {e}")
    st.error(
        "This might be due to a missing library. Please ensure you have run: pip install transformers torch streamlit")