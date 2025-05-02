import streamlit as st
from openai import OpenAI
from streamlit_chat import message
from datetime import datetime
import time
import random
import base64

def render_chat():
    # st.title("Group Chat Begins")

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


    # --- agent persona mapping ---
    persona = {
        "Olivia": (
            "You're a warm and socially active liberal who often brings up human stories, empathy, and lived experiences. "
            "You speak casually and are very expressive, with a strong sense of fairness and inclusion."
        ),
        "Curtis": (
            "You're a sharp, sarcastic progressive who follows politics closely and isn’t afraid to critique conservative rhetoric. "
            "You speak in a witty, slightly cynical tone, often using metaphors or pop culture references to make a point."
        ),
        "Mark": (
            "You're a policy-savvy liberal who prefers calm, reasoned discussion. "
            "You value evidence and long-term thinking, and you’re quick to point out slippery logic in arguments. "
            "Your tone is polite but firm. You speak like someone who reads think pieces and congressional reports for fun."
        )
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

    Please enter your name or nickname before joining.
        """)

        user_name = st.text_input("Enter your name or nickname", key="nickname_input")

        if user_name:
            st.session_state.nickname = user_name

        if st.button("Enter Chat", disabled=not user_name):
            preset_messages = [
                ("Curtis", "Hey, so there's another debate flaring up about gun laws. I honestly can't believe people are still arguing over it."),
                ("Olivia", "Exactly, how many more shootings do we need before we pass real reform?"),
                # ("Liam", "I feel like it’s just making everything worse."),
                # ("Shah", "Mmm, it’s definitely leaning in a worrying direction."),
                ("Mark", f"Totally. It's like logic takes a back seat. Anyway, hey {user_name}, welcome to the group! How's it going? Anything thoughts on the issue?")
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
            num_responders = random.randint(1, 3)
            ai_names = random.sample(group_members, k=num_responders)

            # loop
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
                        messages=[{"role": "system", "content": f"{persona[ai_name]} You are in a casual work chat group. "
                                    "Be casual and brief (1 to 3 sentences), and vary your tone and length like real people. "
                                    "Avoid long monologue. React to the group conversation naturally, but do not mention "
                                    f"{st.session_state.nickname} or ask them anything directly. "
                                    "Do not change the topic unless the participant clearly initiates a new one. "
                                    "Stay focused and stay liberal on the current topic and continue building on what others have said. "
                                    "Avoid bringing up unrelated topics like weekend plans or personal activities."}] + context,
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

            # with st.chat_message("assistant"):
            with st.spinner(f"{followup_speaker} is typing..."):
                time.sleep(random.uniform(2.5, 4.0))
                user_name = st.session_state.get("nickname", "you")
                
                prompt_styles = [
                    "Pose a friendly question to {name} to invite them into the conversation.",
                    "Make a casual observation that might get {name} to jump in.",
                    "Gently nudge {name} to share what they think.",
                    "Mention {name} naturally in a way that encourages them to respond.",
                    "Say something that includes {name} and would likely prompt a reply, even if not a question."
                ]
                style = random.choice(prompt_styles)
                followup_prompt = (
                    f"{persona[followup_speaker]} You're in a casual work chat group. "
                    "Be casual and brief (1 to 3 sentences), and vary your tone and length like real people. "
                    "Vary your message length. Some replies should be one short sentence. Some can be longer. Avoid sounding robotic or formulaic."
                    "Do not change the topic unless the participant clearly initiates a new one. "
                    "Stay focused and stay liberal on the current topic and continue building on what others have said. "
                    "You are a liberal. Maintain your liberal stance even if others express centrist views. You can acknowledge, but do not shift your position. Stay polite and constructive, but firm in your ideological beliefs."
                    "Avoid bringing up unrelated topics like weekend plans or personal activities. "
                    "Avoid repeating points already said. Don’t restate your own prior comments."
                    f"Your teammate’s name is Olivia, Curtis, and Mark. Do not invent or substitute any other names. "
                    f"Use {st.session_state.nickname}'s name in a natural way to nudge them to join the conversation. "
                    f"{style.replace('{name}', st.session_state.nickname)}"
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

                timestamp = datetime.now().strftime("%H:%M")
                message(
                    f"**{followup_speaker}:** {reply}\n\n<i style='color:gray; font-size: 0.8em'>{timestamp}</i>",
                    is_user=False,
                    key=f"ai_msg_{len(st.session_state.messages)}_{followup_speaker}",
                    logo=avatar_url(followup_speaker),
                    allow_html=True
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "speaker": followup_speaker,
                    "content": reply,
                    "timestamp": timestamp
                })

            st.rerun()


        # check for conversation end
        user_msg_count = sum(1 for m in st.session_state.messages if m["role"] == "user")

        if (
            user_msg_count >= 3
            and not st.session_state.get("final_block_executed", False)
            and st.session_state.page != "post"
        ):
            st.session_state.final_block_executed = True
            st.session_state.page = "post"
            st.rerun()

