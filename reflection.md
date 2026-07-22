# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it? 

The game was set on difficulty normal the first time with 7 attempts allowed to guess a number between 1 and 100. There was a developer debug info menu that showed secret, attempts, score, difficulty, and history. There was an option to enter a guess number, submit guess, new game, and a checkmarked show hint box. There was a history that was logging each guess attempt and the hint was telling me to guess lower with each guess.


- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").  
  1. The first concrete bug I noticed was that on the Normal difficulty setting level, there were 7 attempts allowed to guess a number between 1 and 100 while the Easy difficulty level allowed 5 attempts to guess a number a number between 1 and 100. Lowering the difficulty resulted in less opportunity (guess attempts) to guess the number with the same range of 1 to 100, which actually makes the game harder as the difficulty level is set to an easier diffuclty level. There should be more guess attempts allowed when the difficlty level is changed from normal to easy. 
  2. The second concrete bug I noticed was that the Normal difficulty level required guessing a number from 1 to 100 while the Hard difficulty level required guessing a number from 1 to 50. When the range of numbers to guess is smaller and there is less chance of guessing the wrong number, the game actually becomes easier on the Hard difficulty level. Therefore, there should be a range greater than 1 to 100 to guess on the hard difficulty level rather than the existing 1 to 50 range of numbers to guess. 

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed. 
1. The first bug that I noticed was that the hint always asked me to guess a lower number no matter how low I got as I guessed 50, 20, 10, 5, 3, and 2. The secret number to guess was 91, so the application was telling me to guess a lower number each time when I was supposed to be guessing a higher number with each attempt. 
2

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|50, 20, 10, 5, 3, and 2 |Expected Go Higher Hint | Actual Go Lower Hint Always | Out of attempts! The secret was 91.|

|New Game after completing game. Entered new number. | Recording New Input and Giving Hints. | System says to start a new game to play again, but doesn't register new input and doesn't record guess attempts. | Console states You already won. Start a new game to play again despite attempts to start a new game.|

|Selecting New Game in the middle of current game. | Expected that all history of previous guess attempts will be deleted when a new game starts. | History of previous attempts from previous game are retained upon starting new game. | No console output/error despite the developer debug info showing that guess attempts from previous game are still a part of record. |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? 

I used Claude for this project and added app.py and logic_utils.py as context. Claude gave me the option to diagnose and treat one bug at a time. 

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

AI helped pinpoint the secret keeps changing statebug by pinpointing the following code in app.py: (if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret). 
The AI was correct in pinpointing this bug as on even attempts, the code is comparing an integer guess against a string 50% of the time. That is making the secret change. Working with the AI tool, I have learned that we should always be passing an integer into check_guess everytime so the correct code for even attempts should be: attempts % 2 == 0:
            secret = int(st.session_state.secret).

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result). 

One example of an AI suggestion that was incorrect or misleading was that AI was stating that there was a hints lie bug. AI was stating that in app.py:32=47, guess (int) would be compared to secret (str), and that Python 3 would raise a Type Error that would result in a jump to the except block at line 41. I verified the result by looking in the app.py file, this was lines 36 to 40: 

try:
        if guess > secret:
            return "Too High", "📈 Go HIGHER!"
        else:
            return "Too Low", "📉 Go LOWER!"

As you can see, the Type Error is not creating the hints lie bug. The actual problem is that if the guess is higher than the secret, return "Go HIGHER" would always show the wrong hint and should actually be return "Go LOWER". This also applies to if the guess is lower than the secret, return "Go LOWER" should actually be "Go HIGHER" to provide an accurate bug fix. 

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed? 
I reviewed the change for a bug that the AI wanted to fix, approved the change after I reviewed the diff myself. I then told the AI to generate a pytest case to target the bug that was just fixed. I ran pytest in terminal and ran the app with streamlit run app.py to confirm the fix works in the live game. I found that my new test passed along with existing starter tests. 

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code. 
  I ran pytest for fixing the backward hints bug, as the new tests call check_guess directly and assert on the hint text itself rather than just the outcome label. All five new tests passed, which showed the fix for the bug worked. This helped me confirm that the Too High or Too Low outcome labels were not the issue, rather the message LOWER or HIGHER were the actual problems. I did the Streamlit run app.py test to test the live game and can confirm that the hints would accurately tell me to go higher when my guess was too low and would tell me to go lower when my guess was too high. 

- Did AI help you design or understand any tests? How?  
  AI helped me design and understand the pytest as I told AI to generate a pytest case for each bug that we fixed together. I then ran the pytest in terminal, to see if the new test cases worked. I confirmed the bug fixes myself by running streamlit app to check if the bug fixes were successful. 


---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit? 

I would tell my friend that Streamlit app runs the entire application script from top to bottom every single time that a user interacts with the application like clicking a button or entering an input like a guess. Since the script starts over every time this happens, the normal variables are recreated again with a full reset, so this is why the secret number kept on resetting and the game felt broken. The session state is the Streamlit app's way of remembering things between each rerun (each user interaction) so the values put in st.session_state survive through each user interaction instead of being wiped. They are wiped when the user clicks new game. I learned to fix this by collaborating with the AI agent to store the game's important data in the session state and only generate the secret once rather than having it regenerate with every user interaction. 

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects? 

One habit from this project that I want to reuse is to fix one bug at a time and writing a pytest case that targets each fix before moving on. If you fix all the bugs at once, it is hard to tell what changes fixed each specific issue and there is a possibility of introducing a new bug. On this project, I diagnosed a single bug, reviewed the diff myself, generated a test for it, and confirmed it in both pytest and the live Streamlit app. This one at a time approach helped me from introducing new bugs, which could have created an infinite loop of fixing bugs and introducing new ones. I also want to keep reviewing every AI diff before approving as AI can make mistakes and I correct it's thinking and process so that I can collaborate with AI more efficiently. 

  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task? 

Next time, I would verify the AI's diagnosis of issues against the actual code before reviewing AI diffs. If there is no issue or if AI has the wrong process about why a bug exists, there exists a risk of introducing a new bug or fixing the bug in an incomplete way. On this project, the AI claimed the backwards hints bug came from a TypeError in the try/except block, but when I reviewed the lines myself the real problem was just the Higher/Lower messages being swapped. I'd ask AI to point to the exact lines that it found problematic and explain its reasoning so I can catch the confident but wrong hallucination explanations earlier. 

- In one or two sentences, describe how this project changed the way you think about AI generated code. 

This project showed me that AI and AI-generated code can look polished and ready with confidence, but AI can actually make mistakes that requires a human being to review and ensure that the code is working properly. I now treat AI code as a rough draft rather than the final answer as it is a partner that can help me identify issues earlier, but I still need to rely on my own testing and code review to decided whether a bug has actually been fixed or not. 
