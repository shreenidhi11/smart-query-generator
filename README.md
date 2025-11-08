# Query Generator

Manually creating Boolean queries for LinkedIn or Google searches is tedious and error-prone. Query generator automates this by generating optimized, ready-to-use queries tailored to the role (like “Software Developer” or “Data Engineer”) in seconds.
Job seekers spend hours searching through unstructured posts. Smart Query Generator simplifies this into seconds boosting job search efficiency and cutting down manual effort.

Features:

    1. Improves Search Accuracy -  Builds complex Boolean queries that adhere to LinkedIn’s operator limits
    2. Instant LinkedIn and Google Integration - With one click, users can go directly to LinkedIn and Google search results sorted by latest posts
    3. Saves Time for Job Seekers - This helps users find the most relevant and recent job postings instantly
    4. Suggests alternative job titles - Uses LLM to provide alternative professional job titles with focus on realistic variations used in job postings
    5. Quick response - Uses Redis caching to fetch linkedin queries for repeated job titles

Steps to run this project on your machine

    Run redis docker container : docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
    Run the requirements.txt file : pip -r requirements.txt
    Run the main.py file : uvicorn server:app --reload
    Run the streamlit UI: streamlit run app.py

Technologies Used:

    •	Programming Language: Python
    •	LLM/Embedding API: gemini-2.5-flash
    •	ReactJS - For User Interface
    •	Redis docker container - For caching similar or same user queries

<img width="814" height="886" alt="Image" src="https://github.com/user-attachments/assets/786eec2b-1e67-4f73-a307-d45f02cd7aa7" />
