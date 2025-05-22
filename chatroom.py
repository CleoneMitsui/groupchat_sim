import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from datetime import datetime
from topics import get_random_topic_and_messages
from personas import personas
import time
import random
import base64

if st.button("Reset session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


if "agent_rounds_raw" not in st.session_state:
    st.session_state.agent_rounds_raw = []


def render_chat():
    import streamlit.components.v1 as components

    # warning banner
    st.markdown(
        "<p style='color:red; font-weight:bold;'>⚠️ Please do not refresh the page. Doing so will restart the study and erase your answers.</p>",
        unsafe_allow_html=True
    )

    # block F5 and Ctrl+R
    components.html(
        """
        <script>
        document.addEventListener("keydown", function (e) {
            if ((e.key === "F5") || (e.ctrlKey && e.key === "r")) {
                e.preventDefault();
                alert("Please do not refresh the page. Doing so will restart the study and erase your answers.");
            }
        });
        </script>
        """,
        height=0
    )

    if "awaiting_post" not in st.session_state:
        st.session_state.awaiting_post = False


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
    group_members = ["Olivia", "Curtis", "Mark"]

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



    # --- instruction page ---
    if not st.session_state.entered_chat:
        st.subheader("Instructions")
        st.markdown("""
    You are a **new employee** who just joined a new workplace.
    Some of your colleagues have created a **casual chat group**. It is not a professional channel, but something they created to chat about anything from the weather to social gatherings, exchange ideas, or just everyday stuff.

    You've just been added to this group chat.
    When you enter, you’ll first see the last few messages that have already taken place.
    Feel free to jump in at any time.

    Please enter your name or nickname before joining.
        """)

        user_name = st.text_input("Enter your name or nickname (max 15 characters)", key="nickname_input")

        if user_name:
            if len(user_name) > 15:
                st.warning("Nickname must be 15 characters or fewer.")
            else:
                st.session_state.nickname = user_name
        
        if st.button("Enter Chat", disabled=not user_name or len(user_name) > 15):
            # assign liberal or conservative group
            if "group_ideology" not in st.session_state:
                st.session_state.group_ideology = random.choice(["liberal", "conservative"])

            # get one topic and its messages
            topic_key, preset_messages = get_random_topic_and_messages(st.session_state.group_ideology, user_name)
            st.session_state.selected_topic = topic_key

            for speaker, line in preset_messages:
                st.session_state.messages.append({
                    "role": "assistant",
                    "speaker": speaker,
                    "content": line,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "timestamp_unix": time.time()
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

            #for display only the h and m
            try:
                dt = datetime.strptime(msg["timestamp"], "%H:%M:%S")
            except ValueError:
                dt = datetime.strptime(msg["timestamp"], "%H:%M")

            clean_timestamp = dt.strftime("%H:%M")

            timestamp = f"<i style='color:gray; font-size: 0.8em;'>{clean_timestamp}</i>"


            # timestamp = f"<i style='color:gray; font-size: 0.8em;'>{msg['timestamp']}</i>"


            message(
                f"**{name}:** {msg['content']}\n\n{timestamp}",
                is_user=is_user,
                key=f"msg_{i}",
                logo=logo,
                allow_html=True
            )





        #### USER INPUT (participant input) ####
        # store reaction time using unix timestamp
        user_input = st.chat_input("Type your message here...")
        if user_input:
            now = time.time()  # record current time in Unix timestamp

            # find last assistant message timestamp
            assistant_times = [
                m["timestamp_unix"]
                for m in reversed(st.session_state.messages)
                if m["role"] == "assistant" and "timestamp_unix" in m
            ]
            if assistant_times:
                reaction_sec = now - assistant_times[0]
            else:
                reaction_sec = ""

            # save reaction time
            if "reaction_times" not in st.session_state:
                st.session_state.reaction_times = []
            st.session_state.reaction_times.append(reaction_sec)

            # save user message with both readable and unix timestamp
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "timestamp_unix": now
            })




            # make sure response1 is the part of round 1
            if st.session_state.user_count == 0:
                st.session_state.messages[-1]["temp_round_marker"] = True


            # collect and store the previous round's AI responses before clearing
            round_text = [
                f"{m['speaker']}: {m['content']}"
                for m in st.session_state.messages
                if m.get("temp_round_marker") and m["role"] == "assistant"
            ]
            if round_text:
                st.session_state.agent_rounds_raw.append("\n".join(round_text))

            # now clear the temp_round_marker for the new round
            for m in st.session_state.messages:
                m.pop("temp_round_marker", None)


            st.session_state.user_count += 1

            # check if it is the 5th time BEFORE any AI agent replies
            if st.session_state.user_count >= 5:
                st.session_state.awaiting_post = True
                st.rerun()
            else:
                st.session_state.trigger_ai_reply = True
                st.rerun()


        # AI agent response
        if st.session_state.trigger_ai_reply and st.session_state.user_count <= 6:
            st.session_state.trigger_ai_reply = False

            # ensures everyone sends one message
            ai_names = group_members.copy()
            random.shuffle(ai_names)  # randomise message order

            # store recent assistant replies to avoid repetition
            recent_ai_texts = [m["content"] for m in st.session_state.messages if m["role"] == "assistant"][-10:]

            # detect if someone was directly called
            def get_called_name(messages, members):
                import re
                for m in reversed(messages[-3:]):  # check recent messages
                    if m["role"] == "user":
                        source = m["content"]
                    elif m["role"] == "assistant" and m.get("speaker") not in members:
                        source = m["content"]
                    else:
                        continue  # skip AI agents talking to others (self-mentions)
                    for name in members:
                        pattern = re.compile(rf"\b{name}\b", re.IGNORECASE)
                        if pattern.search(source):
                            return name
                return None



            # get who was called
            called_name = get_called_name(st.session_state.messages, group_members)

        

            # add a helper to let GPT infer who should respond
            def infer_recipient(messages):
                context = messages[-6:]  
                chat = "\n".join(
                    [f"{m.get('speaker', 'You')}: {m['content']}" for m in context]
                )
                system_prompt = (
                    "You are a reasoning agent in a group chat. "
                    "Given the recent messages, infer who should be the next person to respond. "
                    "Only respond with one of these names: Olivia, Curtis, Mark — or respond with 'all' if it should be general."
                )
                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": chat}
                    ],
                    temperature=0.3
                )
                reply = response.choices[0].message.content.strip()
                reply = reply.replace("—", "...")  # replace em dash with ...
                return reply

            recipient = infer_recipient(st.session_state.messages)
            if recipient in group_members:
                ai_names = [recipient]
            else:
                ai_names = group_members.copy()
                random.shuffle(ai_names)

            # if someone was called out by name, force them to respond and skip the rest
            if called_name and called_name in group_members:
                ai_names = [called_name]  # only that person replies
            else:
                ai_names = group_members.copy()
                random.shuffle(ai_names)

            # choose 1–3 AI responders per round
            if called_name and called_name in group_members:
                # if a specific name was mentioned, only that agent replies
                ai_names = [called_name]
            else:
                # otherwise, choose 1–3 random responders
                num_responders = random.randint(1, 3)
                ai_names = random.sample(group_members, k=num_responders)





            # loop
            ##### REGULAR AI RESPONSE BLOCK ####
            for i, ai_name in enumerate(ai_names):
                if i == 0:
                    time.sleep(2)  # <-- fake "thinking" delay before the 1st agent only

                # with st.chat_message("assistant"):
                with st.spinner(f"{ai_name} is typing{'.' * random.randint(1, 3)}"):
                    time.sleep(random.uniform(2.5, 4.5))
                    context = [
                        {"role": "assistant", "content": m["content"]} if m["role"] == "assistant"
                        else {"role": "user", "content": m["content"]}
                        for m in st.session_state.messages[-6:]
                    ]

                    response = client.chat.completions.create(
                        model="gpt-4.1",
                        messages=[{"role": "system", "content": (
                            f"{personas[st.session_state.group_ideology][ai_name]} "
                            f"You are {ai_name} in a casual workplace chat group. "
                            "Speak only as yourself. Do not speak for the group or refer to others as 'we'. "
                            "Respond naturally as if in a group chat. Be casual and brief. "
                            "Vary your tone and length like real people. Do not use em dashes (—). "
                            "Do not ask the participant a direct question or mention their name. "
                            "Do not change topics unless the participant clearly does. "
                            "Stay focused on the current topic and build on what others said. "
                            "Maintain your ideological stance. Acknowledge differing views if needed, but do not shift your position. "
                            "Avoid personal talk like weekend plans or small talk."
                        )}] + context,

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

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    display_time = datetime.now().strftime("%H:%M")
                    message(
                        f"**{ai_name}:** {reply}\n\n<i style='color:gray; font-size: 0.8em'>{display_time}</i>",
                        is_user=False,
                        key=f"ai_msg_{len(st.session_state.messages)}_{ai_name}",
                        logo=avatar_url(ai_name),
                        allow_html=True
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "speaker": ai_name,
                        "content": reply,
                        "timestamp": timestamp,
                        "timestamp_unix": time.time(),
                        "temp_round_marker": True
                    })
                if i < len(ai_names) - 1:
                    time.sleep(random.uniform(1.5, 3.0))

            # END of 1-3 agents' replies → do 1 more follow-up
            # get last agent speaker (the final agent who replied)
            last_assistant = None
            for m in reversed(st.session_state.messages):
                if m["role"] == "assistant":
                    last_assistant = m["speaker"]
                    break

            # make sure the follow-up speaker is not the last assistant
            followup_candidates = [name for name in group_members if name != last_assistant]
            followup_speaker = random.choice(followup_candidates)

            time.sleep(1.5)




            ##### FOLLOW-UP NUDGING MESSAGE BLOCK #####
            # with st.chat_message("assistant"):

            with st.spinner(f"{followup_speaker} is typing..."):
                time.sleep(random.uniform(2.5, 4.0))
                user_name = st.session_state.get("nickname", "you")
                
                # --- follow-up prompt styles per agent ---
                prompt_styles_olivia = [
                    "Say something empathetic or personal that might encourage {name} to jump in.",
                    "Bring up a human side of the topic and naturally include {name} in your thought.",
                    "Use a soft tone and curiosity to invite {name}'s opinion.",
                ]

                prompt_styles_curtis = [
                    "Drop a sarcastic or witty remark that might get {name}'s attention.",
                    "Make a pointed pop culture reference and include {name} casually.",
                    "Say something a bit bold or edgy that {name} might want to respond to.",
                ]

                prompt_styles_mark = [
                    "Make a thoughtful or analytical comment and politely invite {name} to weigh in.",
                    "Point out a logical flaw or subtle contradiction and nudge {name} to comment.",
                    "Refer to evidence or policy implications and casually ask what {name} thinks.",
                ]
                
                # choose appropriate style based on speaker
                if followup_speaker == "Olivia":
                    style = random.choice(prompt_styles_olivia).replace("{name}", st.session_state.nickname)
                elif followup_speaker == "Curtis":
                    style = random.choice(prompt_styles_curtis).replace("{name}", st.session_state.nickname)
                else:
                    style = random.choice(prompt_styles_mark).replace("{name}", st.session_state.nickname)

                followup_prompt = (
                    f"{personas[st.session_state.group_ideology][followup_speaker]} "
                    f"You are {followup_speaker} in a casual work chat group. "
                    "Speak only as yourself. Do not represent the group or refer to others as 'we'. "
                    "Be casual and brief, and vary your tone and length like real people. "
                    "Avoid sounding robotic or formulaic. Do not use em dashes (—). "
                    "Stay on topic unless the participant changes it. "
                    "Maintain your ideological stance. You can acknowledge differing views politely, but do not shift your position. "
                    "Do not ask the participant a direct question, but include them in your comment naturally. "
                    "Do not invent any other names outside this group."
                    f"{style}"
                )



                context = []
                for m in st.session_state.messages:
                    if m["role"] == "assistant":
                        context.append({"role": "assistant", "content": m["content"]})

                # (read the last 20 messages)
                context = context[-20:]


                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[{"role": "system", "content": followup_prompt}] + context,
                    temperature=0.8
                )
                reply = response.choices[0].message.content.strip()

                timestamp = datetime.now().strftime("%H:%M:%S")
                display_time = datetime.now().strftime("%H:%M")
                message(
                    f"**{followup_speaker}:** {reply}\n\n<i style='color:gray; font-size: 0.8em'>{display_time}</i>",
                    is_user=False,
                    key=f"ai_msg_{len(st.session_state.messages)}_{followup_speaker}",
                    logo=avatar_url(followup_speaker),
                    allow_html=True
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "speaker": followup_speaker,
                    "content": reply,
                    "timestamp": timestamp,
                    "timestamp_unix": time.time(),
                    "temp_round_marker": True  # used to group per round
                })


            st.rerun()


        # check for conversation end
        user_msg_count = sum(1 for m in st.session_state.messages if m["role"] == "user")

    if st.session_state.awaiting_post:
        st.markdown("*That is the end of the study.*")
        time.sleep(1)  # gives user a moment
        st.session_state.page = "post"
        st.session_state.awaiting_post = False

        # collect and store current round's replies only
        round_text = [
            f"{m['speaker']}: {m['content']}"
            for m in st.session_state.messages
            if m.get("temp_round_marker") and m["role"] == "assistant"
        ]

        if round_text:
            st.session_state.agent_rounds_raw.append("\n".join(round_text))



        for m in st.session_state.messages:
            m.pop("temp_round_marker", None)


        st.rerun()
