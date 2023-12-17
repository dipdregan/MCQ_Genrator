import os
import pandas as pd

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback

from src.mcqgenrator.logger import logging
from src.mcqgenrator.templates import TEMPLATE_FOR_QUERY,TEMPLATE_FOR_OUT_PUT
from dotenv import load_dotenv

load_dotenv()

Key = os.getenv('OPENAI_API_KEY')


llm = ChatOpenAI(openai_api_key = Key, model_name='gpt-3.5-turbo', temperature=0.7)

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE_FOR_QUERY
    )

quiz_chain = LLMChain(
                    llm=llm,
                    prompt=quiz_generation_prompt,
                    output_key='quiz',
                    verbose=True
                    )


quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], 
                                      template=TEMPLATE_FOR_OUT_PUT)

review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)


# This is an Overall Chain where we run the two chains in Sequence
generate_evaluate_chain=SequentialChain(
                chains=[quiz_chain, review_chain],
                input_variables=["text", "number", "subject", "tone", "response_json"],
                output_variables=["quiz", "review"],
                verbose=True,
                )

