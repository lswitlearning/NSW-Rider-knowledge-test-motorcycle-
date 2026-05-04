import streamlit as st
import json
import os
import random

# 1. Load Data
@st.cache_data
def load_data():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_data()

# 2. Initialize Session State
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.is_correct = None # Tracks if the current answer is correct

# 💡 Core Improvement: Shuffle options every time a new question is loaded
if "current_options" not in st.session_state or st.session_state.new_q:
    q = questions[st.session_state.q_index]
    # Identify the correct answer (always the first one in the original list)
    correct_text = q["options"][0]
    
    # Create a copy and shuffle the options
    opts = q["options"].copy()
    random.shuffle(opts)
    
    # Store shuffled options and correct answer text in session state
    st.session_state.current_options = opts
    st.session_state.correct_text = correct_text
    st.session_state.new_q = False

st.title("🚗 Driver Knowledge Test")

# Get data for the current question
q = questions[st.session_state.q_index]

# Display Progress
st.write(f"Question {st.session_state.q_index + 1} / {len(questions)}")

# --- Display Image (Scaled down) ---
if q.get("image"):
    img_path = os.path.join("quiz_images", q["image"])
    if os.path.exists(img_path):
        st.image(img_path, width=250) 

st.subheader(q["question"])

# --- Question & Answer Area ---
if not st.session_state.answered:
    # Display radio buttons with shuffled options
    selected = st.radio("Select your answer:", st.session_state.current_options, key=f"r_{st.session_state.q_index}")
    
    if st.button("Submit Answer"):
        st.session_state.answered = True
        # Check if the selected text matches the correct answer[cite: 1]
        if selected == st.session_state.correct_text:
            st.session_state.score += 1
            st.session_state.is_correct = True
        else:
            st.session_state.is_correct = False
        st.rerun()

# --- Display Results (Persistent Feedback) ---
else:
    if st.session_state.is_correct:
        st.success("✅ Correct")
    else:
        st.error("❌ Incorrect")
        st.info(f"The correct answer was：{st.session_state.correct_text}")
    
    if st.button("ext Question"):
        if st.session_state.q_index < len(questions) - 1:
            st.session_state.q_index += 1
            st.session_state.answered = False
            st.session_state.new_q = True # Mark for next shuffle
            st.rerun()
        else:
            st.balloons()
            st.success(f"🎊 Quiz Completed! Final Score:{st.session_state.score} / {len(questions)}")
            if st.button("Restart Quiz"):
                st.session_state.q_index = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.new_q = True
                st.rerun()