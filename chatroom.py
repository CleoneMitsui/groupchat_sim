import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from datetime import datetime
import time
import random
import base64

st.set_page_config(page_title="Group Chat", page_icon="💬")
st.title("Study 1a Chat Group Test")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- session initiation ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "entered_chat" not in st.session_state:
    st.session_state.entered_chat = False
if "user_logo" not in st.session_state:
    st.session_state.user_logo = ""
if "user_count" not in st.session_state:
    st.session_state.user_count = 0
if "trigger_ai_reply" not in st.session_state:
    st.session_state.trigger_ai_reply = False


# --- AI agents utilities ---
group_members = ["Olivia", "Liam", "Curtis", "Ava", "Shah"]

def avatar_url(name):
    try:
        with open(f"images/{name}.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{encoded}"
    except FileNotFoundError:
        return f"https://api.dicebear.com/6.x/icons/svg?seed={name}"

def load_user_logo():
    with open("images/user.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"


# --- agent persona mapping ---
persona = {
    "Olivia": "You're a casually liberal colleague, riendly and talkative.",
    "Curtis": "You're a sarcastic but progressive dude from university.",
    "Liam": "You're a quiet but thoughtful teammate who leans liberal.",
    "Shah": "You're a curious neutral voice in the group, leans liberal.",
    "Ava": "You're a moderate, polite and skeptical about the conservatives."
}

# --- instruction page ---
if not st.session_state.entered_chat:
    st.subheader("Instructions")
    st.markdown("""
You are a **new employee** who just joined a new workplace.
Some of your colleagues have created a **casual chat group**. It is not a professional channel, but something they created to chat about anything from the weather to social gatherings, exchange ideas, or just everyday stuff.

You've just been added to this group chat.
When you enter, you’ll first see the last few messages that have already taken place.
Feel free to jump in at any time.
    """)
    if st.button("Enter Chat"):
        preset_messages = [
            ("Olivia", "Hey, did you all see the thing about the new healthcare bill?"),
            ("Curtis", "Yeah... I honestly don’t get how anyone could support it."),
            ("Shah", "I feel like it’s just making everything worse.")
        ]
        for speaker, line in preset_messages:
            st.session_state.messages.append({
                "role": "assistant",
                "speaker": speaker,
                "content": line,
                "timestamp": datetime.now().strftime("%H:%M")
            })
        st.session_state.user_logo = load_user_logo()
        st.session_state.entered_chat = True
        st.rerun()



# --- main chat UI ---
else:
    st.subheader("Group Chat Begins 💬")
    st.markdown(f"👥 **Members:** {', '.join(group_members)} and **You**")

    # SHOW ALL MESSAGES
    for i, msg in enumerate(st.session_state.messages):
        is_user = msg["role"] == "user"
        logo = st.session_state.user_logo if is_user else avatar_url(msg["speaker"])
        name = "You" if is_user else msg["speaker"]
        timestamp = f"<i style='color:gray; font-size: 0.8em;'>{msg['timestamp']}</i>"
        message(
            f"**{name}:** {msg['content']}\n\n{timestamp}",
            is_user=is_user,
            key=f"msg_{i}",
            logo=logo,
            allow_html=True
        )

    # user input (participant input)
    user_input = st.chat_input("Type your message here...")
    if user_input:
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        st.session_state.user_count += 1
        st.session_state.trigger_ai_reply = True
        st.rerun()

    # AI agent response
    if st.session_state.trigger_ai_reply and st.session_state.user_count <= 6:
        st.session_state.trigger_ai_reply = False
        
        # randomly have 1, 2, or 3 replies at once
        # num_replies = random.choices([1, 2, 3], weights=[0.7, 0.3, 0.1])[0]

        # recent_speakers = {m["speaker"] for m in st.session_state.messages[-5:] if m["role"] == "assistant"}
        # available_names = [n for n in group_members if n not in recent_speakers]

        # # fallback: if too few left, use full group
        # if len(available_names) < num_replies:
        #     available_names = list(set(group_members) - recent_speakers)
        #     num_replies = min(num_replies, len(available_names))

        # random.shuffle(available_names)
        # ai_names = available_names[:num_replies]

        # ensures everyone sends one message
        ai_names = group_members.copy()
        random.shuffle(ai_names)  # randomise message order


        for i, ai_name in enumerate(ai_names):
            if i == 0:
                time.sleep(2)  # <-- fake "thinking" delay before the 1st agent only

            with st.chat_message("assistant", avatar=avatar_url(ai_name)):
                with st.spinner(f"{ai_name} is typing{'.' * random.randint(1, 3)}"):
                    time.sleep(random.uniform(2.5, 4.5))
                    context = [
                        {"role": "assistant", "content": m["content"]} if m["role"] == "assistant"
                        else {"role": "user", "content": m["content"]}
                        for m in st.session_state.messages[-6:]
                    ]

                    response = client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[{"role": "system", "content": f"{persona[ai_name]} You are in a casual work chat group. Be casual and brief (1–3 sentences), and vary your tone and length like real people. Avoid long monologues. Occasionally, end your message with a short, natural question to keep the conversation flowing."}] + context,
                        temperature=0.7
                    )
                    reply = response.choices[0].message.content.strip()
                    # recursively remove any group member names at the beginning
                    while True:
                        for other_name in group_members:
                            if reply.startswith(f"{other_name}:"):
                                reply = reply[len(f"{other_name}:"):].strip()
                                break
                        else:
                            break  # no prefix matched

                    timestamp = datetime.now().strftime("%H:%M")
                    message(
                        f"**{ai_name}:** {reply}\n\n<i style='color:gray; font-size: 0.8em'>{timestamp}</i>",
                        is_user=False,
                        key=f"ai_msg_{len(st.session_state.messages)}_{ai_name}",
                        logo=avatar_url(ai_name),
                        allow_html=True
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "speaker": ai_name,
                        "content": reply,
                        "timestamp": timestamp
                    })
            if i < len(ai_names) - 1:
                time.sleep(random.uniform(1.5, 3.0))
        st.rerun()

    # END MESSAGE (end the conversation after 6 user inputs)
    user_msg_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    if user_msg_count >= 6:
        st.markdown("<hr><p style='text-align:center'><b>Thank you for participating.</b></p>", unsafe_allow_html=True)
        st.stop()
