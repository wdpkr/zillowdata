import pandas as pd
import streamlit as st
import numpy as np

def print_hello(name = 'World'):
    st.write(f'## Hello, {name}')

name = st.text_input('Name: ', key = 'name')
print_hello(name)

x = np.linspace(-1,1, 1000)
a = st.slider('a')
df = pd.DataFrame(
    dict(
         y = a * np.cos(a * x))
)
st.line_chart(df)


#if __name__ == '__main__':
#    print('Hello')
