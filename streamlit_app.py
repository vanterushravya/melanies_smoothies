# import streamlit as st
# import requests

# #from snowflake.snowpark.context import get_active_session
# from snowflake.snowpark.functions import col

# # Write directly to the app
# st.title("Customize your smoothie!:cup_with_straw:")
# st.write(
#     """Choose the fruits you want in your custom Smoothie!
#     """
# )
# name_on_order=st.text_input('Name on Smoothie!')
# st.write('The name on your Smoothie will be:'
# ,name_on_order)

# #session = get_active_session()
# cnx=st.connection("snowflake")
# session=cnx.session()
# my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# #st.dataframe(data=my_dataframe, use_container_width=True)

# ingredients_list=st.multiselect(
# 'Choose upto 5 ingredients:',my_dataframe,max_selections=5)

# if ingredients_list:
  
#   ingredients_string=''
#   for fruit_chosen in ingredients_list:
#       ingredients_string+=fruit_chosen+' '
#       st.subheader(fruit_chosen + " Nutrition Information")
#       fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
#       fv_df=st.dataframe(data=fruityvice_response.json(),use_container_width=True)
#       my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
#             values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

#   #st.write(my_insert_stmt)
#   #st.stop()
# time_to_insert=st.button('Submit Order')
# if time_to_insert:
#     session.sql(my_insert_stmt).collect()
#     st.success('Your Smoothie is ordered!', icon="✅")

import streamlit as st
import requests
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col

# Initialize Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("Customize your smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# User input for name on order
name_on_order = st.text_input('Name on Smoothie!')
st.write('The name on your Smoothie will be:', name_on_order)

# Retrieve fruit options from Snowflake
try:
    fruit_options_df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
    fruit_options = [row['FRUIT_NAME'] for row in fruit_options_df]
    st.write("Fruit options retrieved:", fruit_options)
except Exception as e:
    st.error(f"Error retrieving fruit options: {e}")
    st.stop()

# Display multiselect for ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_options, max_selections=5)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.write(f"Processing fruit: {fruit_chosen}")
        try:
            st.subheader(f"{fruit_chosen} Nutrition Information")
            
            # Fetching nutrition data from Fruityvice API
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            fruityvice_response.raise_for_status()
            fruit_data = fruityvice_response.json()
            
            # Check if the response contains the expected structure
            if isinstance(fruit_data, list) and fruit_data:
                fruit_data = fruit_data[0]  # Assuming it's a list with one item

            # Displaying the data
            st.write(fruit_data)
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")
        except Exception as e:
            st.error(f"Error processing data for {fruit_chosen}: {e}")

    # Prepare SQL statement to insert order
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (%(ingredients)s, %(name_on_order)s)
    """

    # Insert order into Snowflake
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(my_insert_stmt, {'ingredients': ingredients_string, 'name_on_order': name_on_order}).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Error submitting order: {e}")
else:
    st.write("No ingredients selected yet.")




