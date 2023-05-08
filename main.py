# Import the Libraries``
import io
from zipfile import ZipFile
import pandas as pd
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title='York Archive', layout="wide")
st.title('York Data Archive')

target = st.text_input("Target", "")
folder_choice = st.selectbox('60cm OR 1m?', ('60cm', '1m'))

wget_text = '"drive pull -quiet -id FILEID \n"'


@st.cache(allow_output_mutation=True)
def button_states():
    return {"pressed": None}


# Create the user table
cols = st.columns(10)
submit = cols[0].button('Submit')
download_button = cols[1].button('Download')
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
terminal_input = []
Select_all = cols[2].button('Select All')
UnSelect_all = cols[3].button('UnSelect All')
is_pressed = button_states()
col1, col2, col3, col4, col5 = st.columns((0.7, 3.5, 0.9, 1.3, 1))

col1.write("Image")
col2.write("ID")
col3.write("Target")
col4.write("Date")


def read_zip(zip_fn, extract_fn=None):
    zf = ZipFile(zip_fn)
    if extract_fn:
        return zf.read(extract_fn)
    else:
        return {name: zf.read(name) for name in zf.namelist()}


@st.cache
# Write the bash script
def setup():
    file_dict_1m = pd.read_csv("file_dict_1m.csv")
    file_dict_60cm = pd.read_csv(io.BytesIO(read_zip('file_dict_60cm.zip', 'file_dict_60cm.csv')))
    # file_dict_60cm = pd.read_csv("file_dict_60cm.csv")

    folder_arr = []
    folder_id = []
    folder_indexes = []
    for file_iter in range(len(file_dict_60cm)):
        if file_dict_60cm.type[file_iter] == 'file':
            if target.lower() in str(file_dict_60cm.dir[file_iter]).lower() or target.upper() in str(
                    file_dict_60cm.dir[file_iter]).upper():
                path_list = file_dict_60cm.dir[file_iter].split(os.sep)
                for i in range(len(path_list)):
                    if "+" in path_list[i]:
                        folder_name = path_list[i]
                        folder_arr.append(folder_name)

        if file_dict_60cm.type[file_iter] == 'folder':
            folder_indexes.append(file_iter)

    folder_arr = list(set(folder_arr))
    title_arr = []

    for index1 in range(len(folder_arr)):
        for index2 in range(len(folder_indexes)):
            if str(file_dict_60cm.title[folder_indexes[index2]]) == str(folder_arr[index1]):
                folder_id.append(file_dict_60cm.id[folder_indexes[index2]])
                title_arr.append(file_dict_60cm.title[folder_indexes[index2]])

    image_arr = []
    for i in range(len(folder_id)):
        image_arr.append(str(i))

    return image_arr, folder_id, title_arr


def checkbox():
    data = setup()

    user_table = {
        'Image': data[0],
        'ID': data[1],
        'Target': target,
        'Date': data[2],
    }

    array_checkbox = []

    for i in data[0]:
        array_checkbox.append(str(i))

    if 'dummy_data' not in st.session_state.keys():
        dummy_data = array_checkbox
        st.session_state['dummy_data'] = dummy_data
    else:
        dummy_data = st.session_state['dummy_data']

    if Select_all:
        for i in dummy_data:
            st.session_state['dynamic_checkbox_' + i] = True
        st.experimental_rerun()
    if UnSelect_all:
        for i in dummy_data:
            st.session_state['dynamic_checkbox_' + i] = False
        st.experimental_rerun()

    st.markdown("""
    <style>
    .big-font {
        font-size:15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    for x in dummy_data:
        col2.markdown('<p class="big-font"> ' + user_table['ID'][int(x)] + '</p>', unsafe_allow_html=True)
        col3.markdown('<p class="big-font"> ' + user_table['Target'] + '</p>', unsafe_allow_html=True)
        col4.markdown('<p class="big-font"> ' + user_table['Date'][int(x)] + '</p>', unsafe_allow_html=True)

    for i in dummy_data:
        col1.checkbox(i, key='dynamic_checkbox_' + i)

    Selected_checkboxes = [i.replace('dynamic_checkbox_', '') for i in st.session_state.keys() if
                           i.startswith('dynamic_checkbox_') and st.session_state[i]]

    del st.session_state['dummy_data']

    os.system("> script.sh")

    return Selected_checkboxes, user_table


def script(select_data):
    os.system('chmod 777 script.sh')
    os.system('sh script.sh')
    f = open('script.sh', 'w')

    if download_button:
        for i in range(len(select_data[0])):
            index = int(select_data[0][i])
            f.write(wget_text[1:-1].replace('FILEID', select_data[1]['ID'][index]))
            f.write(wget_text[1:-1].replace('FILEID', select_data[1]['ID'][index]))
            terminal_input.append(str(wget_text[1:-1].replace('FILEID', select_data[1]['ID'][index])))

    f.close()

    return terminal_input


def download():
    select_checkbox = checkbox()

    run_script = script(select_checkbox)

    for i in range(len(run_script)):
        os.system(run_script[i])


if submit:
    is_pressed.update({"pressed": True})

if is_pressed["pressed"]:  # saved between sessions
    download()

# When user presses Download, display test of all .FIT files that are listed for the selected folder(s).
# Automatically input YES when command prompt asks to proceed with the changes
# Using FILEID and ID, direct user to link that download the files automatically


# THE NEXT ITTERATION OF THIS WEB APP WILL BE BUILT IN EITHER A DJANGO(PYTHON BACKEND, JAVASCRIPT FRONTEND) _OR_