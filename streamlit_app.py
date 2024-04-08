# Import python packages
from snowflake.snowpark.functions import col
import streamlit as st
import requests
import pandas

# Write directly to the app
st.title("Smoothie Orders :cup_with_straw:")
st.write("Choose fruits you want in your smoothie.")

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be: ', name_on_order)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ''

    for fruit in ingredients_list:
        ingredients_string += fruit + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit, ' is ', search_on)
        
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit)
        st.subheader(fruit + ' Nutrition Information')
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    my_insert_stmt = """
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')
    """

    

    # st.write(my_insert_stmt)
    # st.stop()
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered, '+ name_on_order +'!', icon="✅")

