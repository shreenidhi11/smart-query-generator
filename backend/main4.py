import streamlit as st
import re
from transformers import pipeline


# --- 1. Load the LLM (Cached) ---
@st.cache_resource
def load_model():
    """Loads the T5 model one time and caches it."""
    return pipeline("text2text-generation", model="google/flan-t5-large")


# --- 2. Query "Ingredients" (NOW RESPECTING LIMITS) ---
# We keep these lists short (<= 4 items) to obey the <= 5 OR clause limit.
ACTION_PHRASES = [
    "hiring",
    "recruiting",
    "join our team",
    "looking for"
]

EXCLUSION_PHRASES = [
    "internship",
    "contract"
]


# --- 3. LLM Synonym Generator (NOW RESPECTING LIMITS) ---
def get_synonyms_from_llm(job_title, generator):
    """
    Uses the LLM to generate synonyms and aggressively cleans the output.
    """

    # We ask for 3-4 synonyms to stay within the 5-term OR limit.
    prompt = f"""
    Task: Generate a list of 3 common synonyms or related job titles for "{job_title}".
    Format: A single line, comma-separated.
    Titles:
    """

    try:
        outputs = generator(prompt, max_length=128, num_return_sequences=1)
        raw_text = outputs[0]['generated_text']

        synonyms = []
        candidates = re.split(r'[,\n]', raw_text)

        for s in candidates:
            synonym = s.strip().title()

            if not synonym: continue
            if len(synonym) > 35: continue
            if synonym.lower() == job_title.lower(): continue

            synonyms.append(synonym)

        # --- LIMITER ---
        # We only take the first 3 synonyms to keep our queries short.
        print(synonyms)
        return list(set(synonyms))[:3]

    except Exception as e:
        st.error(f"Error calling LLM: {e}")
        return []


# --- 4. NEW: Constraint-Aware Query Builder (v6) ---
def build_boolean_queries(main_title, synonyms):
    """
    Builds a *list* of short, safe queries that respect LinkedIn limits.
    """
    queries = []

    # --- Build reusable, safe query parts ---

    # Main title part (1 term)
    main_title_part = f'"{main_title.title()}"'

    # All titles part (max 4 terms, 3 ORs)
    all_titles_list = [main_title.title()] + synonyms
    titles_query_part = f"({' OR '.join([f'"{t}"' for t in all_titles_list])})"

    # All actions part (max 4 terms, 3 ORs)
    actions_query_part = f"({' OR '.join([f'"{p}"' for p in ACTION_PHRASES])})"

    # All exclusions part (max 4 terms, 3 ORs)
    exclusions_query_part = f"NOT ({' OR '.join([f'"{p}"' for p in EXCLUSION_PHRASES])})"

    # --- Generate the query list ---

    # Query 1: Main Title + All Actions (Simple & Effective)
    # Ops: 1 AND + 3 ORs = 4 (SAFE)
    queries.append(f"{main_title_part} AND {actions_query_part}")

    # Query 2: All Titles + "hiring" (Broadest "hiring" search)
    # Ops: 3 ORs + 1 AND = 4 (SAFE)
    queries.append(f'{titles_query_part} AND "hiring"')

    # Query 3: All Titles + "recruiting" (Broad "recruiting" search)
    # Ops: 3 ORs + 1 AND = 4 (SAFE)
    queries.append(f'{titles_query_part} AND "recruiting"')

    # Query 4: Main Title + All Actions + All Exclusions (Most Complex)
    # Ops: 1 AND + 3 ORs + 1 AND + 1 NOT + 3 ORs = 9 (SAFE)
    # This is the longest query we'll make, should be < 250 chars.
    queries.append(f"{main_title_part} AND {actions_query_part} AND {exclusions_query_part}")

    # Query 5: All Titles + All Actions (Riskier, but good to try)
    # Ops: 3 ORs + 1 AND + 3 ORs = 7 (SAFE)
    # This might get long, but operators are fine.
    # queries.append(f"{titles_query_part} AND {actions_query_part}")

    # Query 6: Just All Titles (For manual scanning)
    # Ops: 3 ORs (SAFE)
    # queries.append(f"{titles_query_part}")

    return queries


# --- 5. The Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🚀 Smart Job Query Generator (v6 - Constraint Aware)")
st.markdown(
    "Enter a job title. I'll use an **LLM** for synonyms and generate **short, safe queries** that respect LinkedIn's limits.")
st.info("ℹ️ **Tip:** These queries are designed to be short. Try them one by one in the LinkedIn **Posts** filter.")

try:
    st.toast("Loading AI model... (this may take a moment on first run)")
    generator = load_model()

    job_title = st.text_input("Enter your desired job title:", "Python Developer")

    if st.button("Generate Queries"):
        if not job_title:
            st.error("Please enter a job title.")
        else:
            with st.spinner("🧠 Asking AI for related roles..."):

                synonyms = get_synonyms_from_llm(job_title, generator)

                if synonyms:
                    st.subheader("AI found these related roles (limited to 3):")
                    st.write(", ".join(synonyms))
                else:
                    st.warning(f"The AI didn't return usable synonyms. Building queries with the main title only.")

                st.subheader("Here is your constraint-aware query list:")

                queries_list = build_boolean_queries(job_title, synonyms)

                for i, query in enumerate(queries_list, 1):
                    st.markdown(f"---")
                    st.markdown(f"**Query {i}:**")
                    st.code(query, language="text")
                    st.button("Copy", key=f"copy_{i}", on_click=lambda s=query: st.toast(f"Copied Query {i}!"), args=())

except Exception as e:
    st.error(f"A critical error occurred: {e}")
    st.error(
        "This might be due to a missing library. Please ensure you have run: pip install transformers torch streamlit")