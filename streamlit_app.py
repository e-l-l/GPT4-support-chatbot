import streamlit as st
import chatbot_utils
st.title('ABC Chatbot')

langs=chatbot_utils.getLangs()
names = []
code="en"
for language in langs:
    names.append(language['name'])
with st.sidebar:
    st.write('Please enter your name')
    name = st.text_input('Name')

    langName = st.selectbox(
        "Select Language",
        names,
        index=21,
        label_visibility="visible",
    )
    for language in langs:
        if language['name'] == langName:
            code = language['code']
            break
if name:
    if ("messages" not in st.session_state.keys()):
        st.session_state.messages = [{"role": "ABC", "content": f"Hello! {name}, Welcome to ABC Customer service. How can I help you?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input(disabled=not (name)):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    if st.session_state.messages[-1]["role"] != "ABC":
        with st.chat_message("ABC"):
            with st.spinner():
                response = chatbot_utils.reply(name,prompt,code)
                # response = "This is a test response"
                st.write(response) 
        message = {"role": "ABC", "content": response}
        st.session_state.messages.append(message)