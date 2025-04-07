import streamlit as st
from openai import OpenAI

import time
from datetime import datetime

import random

from streamlit_chat import message





client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


st.title("Study 1a Chat Group Test 2025.4.6")


# Initialize session state
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    st.subheader("Step 1: Describe Your Group Chat")

    group_type = st.selectbox(
        "Who is in this group chat?",
        ["Work colleagues", "University friends", "Sports teammates", "Fellow parents", "Other"]
    )

    st.markdown("Enter nicknames or initials for your group members:")

    name_inputs = []
    for i in range(1, 6):
        name = st.text_input(f"Member {i} name", key=f"name_{i}")
        name_inputs.append(name)

    if st.button("Enter Chat"):
        if all(name_inputs):
            st.session_state.group_type = group_type
            st.session_state.names = name_inputs
            st.session_state.submitted = True
            st.rerun()
        else:
            st.warning("Please fill in all 5 names.")


else:
    st.subheader("Step 2: Group Chat Begins 💬")

    # Show group info
    st.markdown(f"You're chatting with your **{st.session_state.group_type.lower()}**.")
    st.markdown(f"👥 **Group Members:** {', '.join(st.session_state.names)} and **you**")


    agent_personas = {
        st.session_state.names[0]: "You're a casually liberal office colleague. Friendly and talkative.",
        st.session_state.names[1]: "You're a sarcastic but progressive friend from university.",
        st.session_state.names[2]: "You're a quiet but thoughtful teammate who leans liberal.",
        st.session_state.names[3]: "You're a curious neutral voice in the group.",
        st.session_state.names[4]: "You're a moderate, polite and skeptical about politics."
    }

    # Show preset messages only once

    # Always define messages list once
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "preset_done" not in st.session_state:

        preset_messages = [
            (st.session_state.names[0], "Hey, did you all see the thing about the new healthcare bill?"),
            (st.session_state.names[1], "Yeah... I honestly don’t get how anyone could support it."),
            (st.session_state.names[2], "I feel like it’s just making everything worse.")
        ]

        for speaker, line in preset_messages:
            time.sleep(5) # add time for "thinking"
            with st.chat_message("assistant"):
                with st.spinner(f"{speaker} is typing..."):
                    time.sleep(random.uniform(6, 9)) # simulating realistic typing
                    st.markdown(f"{speaker}: {line}  \n{datetime.now().strftime('%H:%M')}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"{speaker}: {line}  \n{datetime.now().strftime('%H:%M')}"
            })

        st.session_state.preset_done = True


    # Show message history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(
                    f"""
                    <div style='text-align: right; background-color: #f0f2f6; padding: 8px 12px; border-radius: 12px; display: inline-block;'>
                        <strong>You:</strong> {msg['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            speaker, line = msg["content"].split(": ", 1)
            with st.chat_message("assistant"):
                st.markdown(f"{speaker}: {line}")



    # Chat input for participant
    user_input = st.chat_input("Type your message here...")
    if user_input:
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        st.session_state.last_user_input = user_input  # Save for context

       
        # Track which AI should speak next
        if "ai_index" not in st.session_state:
            st.session_state.ai_index = 0

        # Pick the next AI name
        ai_name = st.session_state.names[st.session_state.ai_index % len(st.session_state.names)]

        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Prepare chat history for the agent
        chat_context = []
        for msg in st.session_state.messages[-6:]:  # use only recent history
            if msg["role"] == "user":
                chat_context.append({"role": "user", "content": msg["content"]})
            else:
                # Extract speaker name and message
                if ": " in msg["content"]:
                    speaker, content = msg["content"].split(": ", 1)
                    chat_context.append({"role": "assistant", "content": f"{speaker}: {content}"})

        # Get system prompt
        persona_prompt = agent_personas[ai_name]

        with st.chat_message("assistant"):
            with st.spinner(f"{ai_name} is typing..."):
                time.sleep(9 + 6 * (st.session_state.ai_index % 3))  # vary delay a bit (interval between messages)


                # Generate response using OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": persona_prompt},
                        *chat_context
                    ],
                    temperature=0.8
                )

                # Extract reply
                reply = response.choices[0].message.content.strip()
                st.markdown(f"{ai_name}: {reply}")
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"{ai_name}: {reply}  \n {timestamp}"
                })

                from streamlit_chat import message

                message(
                    f"{ai_name}: {reply}  \n\n<i style='color:gray; font-size: 0.8em;'>{timestamp}</i>",
                    is_user=False,
                    key=f"assistant_{st.session_state.ai_index}",
                    avatar_style=None,
                    logo=f"https://api.dicebear.com/6.x/icons/svg?seed={ai_name}"
                )



        # Update for next turn
        st.session_state.ai_index += 1

        st.rerun()
