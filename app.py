import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenrator.utils import read_file, get_table_data

import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenrator.MCQGenrator import generate_evaluate_chain
from src.mcqgenrator.logger import logging

# loading json file
path = os.path.join(os.getcwd(), "Response.json")

with open(path, 'r') as file:
    RESPONSE_JSON = json.load(file)

# creating a title for the app
st.title("MCQs Generator Application with LangChain and OpenAI..🦜⛓️")

# Create a form using st.form
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Upload a PDF or txt file")

    # Input Fields
    mcq_count = st.number_input("No. of MCQs you want to generate", min_value=3, max_value=50)

    # Subject
    subject = st.text_input("Insert Subject", max_chars=20)

    # Quiz Tone
    options = ["Simple", "Medium", "Hard"]
    tone = st.selectbox("Select Complexity Level Of Questions", options)

    # Add Button
    button = st.form_submit_button("Create MCQs")

# Check if the button is clicked and all fields have input
if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("Generating your MCQ...Wait..."):
        try:
            text = read_file(uploaded_file)
            # Count tokens and the cost of API call
            with get_openai_callback() as cb:
                response = generate_evaluate_chain(
                    {
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    }
                )

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("Error")

        else:
            st.write(f"Total Tokens: {cb.total_tokens}")
            st.write(f"Prompt Tokens: {cb.prompt_tokens}")
            st.write(f"Completion Tokens: {cb.completion_tokens}")
            st.write(f"Total Cost: {cb.total_cost}")

            if isinstance(response, dict):
                # Extract the quiz data from the response
                quiz = response.get("quiz", None)
                if quiz is not None:
                    table_data = get_table_data(quiz)
                    if table_data is not None:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)
                        # Display the review in a text box as well
                        st.text_area(label="Review", value=response["review"])

                        # Download button for the generated quiz
                        csv_data = df.to_csv(index=False).encode('utf-8')
                    else:
                        st.error("Error in the table data")

            else:
                st.write(response)

# Move this block outside the st.form() block
if "csv_data" in locals():
    st.download_button(
        label="Download Quiz",
        data=csv_data,
        file_name=f"{subject}_Quiz.csv",
        key="download_button"
    )
