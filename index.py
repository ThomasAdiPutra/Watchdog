import streamlit as st
import pandas as pd
import time

st.title('File Event Monitor')

df = pd.read_csv('events.csv')
df.columns = ['Filename', 'Path', 'Event Type', 'Event Time']
st.dataframe(df)

while True:
    time.sleep(10)
    st.rerun()
