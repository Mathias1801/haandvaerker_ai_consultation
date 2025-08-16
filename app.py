import streamlit as st
import google.generativeai as genai
import os

# Hent API-nøgle fra miljøvariabel
genai.configure(api_key=os.environ.get("GENMI_API_KEY"))

st.title("Håndværker Chat")
kunde_input = st.text_input("Beskriv din opgave:")
if st.button("Generer forslag"):
    response = genai.chat(messages=[{"role": "user", "content": kunde_input}])
    st.write(response.last)
