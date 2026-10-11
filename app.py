from flask import (

    Flask,

    render_template,

    flash,

    request,

    redirect,

    url_for,

    session

)



from werkzeug.security import (

    generate_password_hash,

    check_password_hash

)



from datetime import datetime



import sqlite3



from database import (

    get_connection,

    create_tables

)





# ============================================================

# FLASK APPLICATION

# ============================================================



app = Flask(__name__)



app.secret_key = "interviewai_secret_key_2026"





# ============================================================

# CREATE DATABASE TABLES

# ============================================================



create_tables()





# ============================================================

# QUESTIONS

# ============================================================



QUESTIONS = {



    "Python Developer": [



        "What is the difference between a list and a tuple in Python?",



        "What are Python decorators and where are they used?",



        "Explain the concept of inheritance in Python.",



        "What is the difference between == and is in Python?",



        "What are exceptions and how do you handle them in Python?"



    ],





    "Java Developer": [



        "What is the difference between JDK, JRE and JVM?",



        "Explain the concept of inheritance in Java.",



        "What is method overloading and method overriding?",



        "What is the difference between an interface and an abstract class?",



        "What is exception handling in Java?"



    ],





    "Web Developer": [



        "What is the difference between HTML, CSS and JavaScript?",



        "What is the difference between id and class in HTML?",



        "What is responsive web design?",



        "What is the DOM in JavaScript?",



        "What is the difference between GET and POST requests?"



    ],





    "Software Engineer": [



        "What is the software development life cycle?",



        "What is the difference between a process and a thread?",



        "What are data structures and why are they important?",



        "What is object-oriented programming?",



        "What is the difference between an array and a linked list?"



    ],





    "Data Analyst": [



        "What is data analysis?",



        "What is the difference between mean, median and mode?",



        "What is SQL used for?",



        "What is data visualization?",



        "What is the difference between structured and unstructured data?"



    ],





    "Other": [



        "Tell me about yourself.",



        "What are your main technical skills?",



        "Describe a project you have worked on.",



        "What is one challenge you faced and how did you solve it?",



        "Why are you interested in this career?"



    ]



}





# ============================================================

# ============================================================
# ANSWER EVALUATION
# ============================================================

ANSWER_CRITERIA = {
    "What is the difference between a list and a tuple in Python?": [["list"], ["tuple"], ["mutable"], ["immutable"]],
    "What are Python decorators and where are they used?": [["decorator"], ["function"], ["wrapper"], ["modify", "extend", "behavior"]],
    "Explain the concept of inheritance in Python.": [["inheritance"], ["parent", "base"], ["child", "derived"], ["class"], ["reuse"]],
    "What is the difference between == and is in Python?": [["equality", "equal"], ["identity"], ["value"], ["object"]],
    "What are exceptions and how do you handle them in Python?": [["exception"], ["try"], ["except"], ["finally"], ["raise"]],
    "What is the difference between JDK, JRE and JVM?": [["jdk"], ["jre"], ["jvm"], ["development"], ["runtime"]],
    "Explain the concept of inheritance in Java.": [["inheritance"], ["parent", "base"], ["child", "derived"], ["class"], ["extends"], ["reuse"]],
    "What is method overloading and method overriding?": [["overloading"], ["overriding"], ["method"], ["parameters"], ["compile", "runtime"]],
    "What is the difference between an interface and an abstract class?": [["interface"], ["abstract"], ["implementation"], ["methods"], ["multiple"]],
    "What is exception handling in Java?": [["exception"], ["try"], ["catch"], ["finally"], ["throw", "throws"]],
    "What is the difference between HTML, CSS and JavaScript?": [["html"], ["css"], ["javascript"], ["structure"], ["style"], ["behavior", "interaction"]],
    "What is the difference between id and class in HTML?": [["id"], ["class"], ["unique"], ["multiple"], ["selector"]],
    "What is responsive web design?": [["responsive"], ["screen"], ["device"], ["mobile"], ["media query"], ["layout"]],
    "What is the DOM in JavaScript?": [["dom"], ["document"], ["object"], ["html"], ["tree"]],
    "What is the difference between GET and POST requests?": [["get"], ["post"], ["data"], ["url"], ["body"], ["request"]],
    "What is the software development life cycle?": [["sdlc"], ["requirements"], ["design"], ["development"], ["testing"], ["maintenance"]],
    "What is the difference between a process and a thread?": [["process"], ["thread"], ["memory"], ["resource"], ["independent"], ["lightweight"]],
    "What are data structures and why are they important?": [["data structure"], ["organize"], ["data"], ["efficient"], ["array", "list"]],
    "What is object-oriented programming?": [["object-oriented", "oop"], ["object"], ["class"], ["encapsulation"], ["inheritance"], ["polymorphism"]],
    "What is the difference between an array and a linked list?": [["array"], ["linked list"], ["contiguous"], ["node"], ["memory"], ["pointer"]],
    "What is data analysis?": [["data analysis", "analysis"], ["data"], ["insights"], ["patterns"], ["decision"]],
    "What is the difference between mean, median and mode?": [["mean"], ["median"], ["mode"], ["average"], ["middle"], ["frequency"]],
    "What is SQL used for?": [["sql"], ["database"], ["query"], ["data"], ["retrieve", "insert", "update", "delete"]],
    "What is data visualization?": [["data visualization", "visualization"], ["chart"], ["graph"], ["visual"], ["data"]],
    "What is the difference between structured and unstructured data?": [["structured"], ["unstructured"], ["schema"], ["table"], ["organized"], ["text", "images"]],
    "Tell me about yourself.": [["name", "myself"], ["education", "student", "degree"], ["skill"], ["project"], ["experience", "career"]],
    "What are your main technical skills?": [["python", "java", "javascript", "html", "css", "sql"], ["skill"], ["programming"], ["technology"]],
    "Describe a project you have worked on.": [["project"], ["developed", "built", "created"], ["technology"], ["role", "worked"], ["result", "outcome"]],
    "What is one challenge you faced and how did you solve it?": [["challenge", "problem"], ["solution", "solved"], ["approach"], ["result", "outcome"], ["learned"]],
    "Why are you interested in this career?": [["interest", "interested"], ["career"], ["skills"], ["learn"], ["goal"], ["passion"]],
}

def evaluate_answer(question_text, answer):
    """
    Evaluate the answer using the concepts expected for the question.

    Important:
    - Empty answers, "idk", "I don't know", etc. receive 0.
    - A few matching words do NOT automatically mean a good answer.
    - Scores depend on how many important concepts are actually covered.
    """

    import re

    text = answer.strip().lower()
    words = re.findall(r"[a-z][a-z'-]*", text)

    if not words:
        return 0

    # Clearly indicates that the candidate does not know the answer.
    dont_know_phrases = [
        "idk",
        "i don't know",
        "i do not know",
        "dont know",
        "do not know",
        "not sure",
        "no idea",
        "i have no idea",
        "cannot answer",
        "can't answer",
        "unable to answer",
        "i don't understand",
        "i do not understand"
    ]

    if any(phrase in text for phrase in dont_know_phrases):
        return 0

    # Very short/non-substantive answers should never receive a high score.
    if len(words) < 4:
        return 0

    criteria = ANSWER_CRITERIA.get(question_text)

    if not criteria:
        return 0

    matched_groups = 0

    for group in criteria:
        if any(term.lower() in text for term in group):
            matched_groups += 1

    coverage = matched_groups / len(criteria)

    # A response with no relevant concepts is incorrect.
    if matched_groups == 0:
        return 0

    # Only one isolated keyword is not enough to demonstrate understanding.
    if matched_groups == 1:
        return 10

    # Convert conceptual coverage into a realistic score.
    # The score does NOT depend mainly on answer length.
    if coverage < 0.30:
        score = 20
    elif coverage < 0.45:
        score = 35
    elif coverage < 0.60:
        score = 50
    elif coverage < 0.75:
        score = 65
    elif coverage < 0.90:
        score = 80
    else:
        score = 92

    # A slightly longer explanation can demonstrate completeness,
    # but length alone cannot rescue an irrelevant answer.
    if len(words) >= 25 and coverage >= 0.60:
        score += 3

    if len(words) >= 45 and coverage >= 0.75:
        score += 3

    return min(score, 100)


# HOME

# ============================================================



@app.route("/")

def home():



    return render_template(

        "home.html"

    )





# ============================================================

# REGISTER

# ============================================================



@app.route(

    "/register",

    methods=["GET", "POST"]

)

def register():



    if request.method == "POST":



        # ----------------------------------------------------

        # GET FORM DATA

        # ----------------------------------------------------



        name = request.form.get(

            "name",

            ""

        ).strip()



        email = request.form.get(

            "email",

            ""

        ).strip().lower()



        password = request.form.get(

            "password",

            ""

        )



        confirm_password = request.form.get(

            "confirm_password",

            ""

        )



        terms = request.form.get(

            "terms"

        )





        # ----------------------------------------------------

        # VALIDATION

        # ----------------------------------------------------



        if not name:



            return render_template(

                "register.html",

                error="Please enter your full name."

            )





        if not email:



            return render_template(

                "register.html",

                error="Please enter your email address."

            )





        if not password:



            return render_template(

                "register.html",

                error="Please create a password."

            )





        if len(password) < 6:



            return render_template(

                "register.html",

                error="Password must contain at least 6 characters."

            )





        if password != confirm_password:



            return render_template(

                "register.html",

                error="Passwords do not match."

            )





        if not terms:



            return render_template(

                "register.html",

                error="Please accept the terms and conditions."

            )





        # ----------------------------------------------------

        # INSERT USER

        # ----------------------------------------------------



        connection = get_connection()



        try:



            hashed_password = generate_password_hash(

                password

            )



            # Support both the existing database schema and the
            # newer schema that includes created_at.
            user_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }

            if "created_at" in user_columns:
                connection.execute(
                    """
                    INSERT INTO users
                    (name, email, password, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        hashed_password,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
            else:
                connection.execute(
                    """
                    INSERT INTO users
                    (name, email, password)
                    VALUES (?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        hashed_password
                    )
                )

            connection.commit()





        except sqlite3.IntegrityError:



            connection.close()



            return render_template(

                "register.html",

                error="An account with this email already exists."

            )





        except Exception as error:



            connection.close()



            print(

                "REGISTRATION ERROR:",

                error

            )



            return render_template(

                "register.html",

                error="Something went wrong while creating your account."

            )





        connection.close()





        # ----------------------------------------------------

        # SUCCESS

        # ----------------------------------------------------



        flash(
            "Account created successfully! Please login to continue.",
            "success"
        )

        return redirect(
            url_for("login")
        )





    # --------------------------------------------------------

    # GET REQUEST

    # --------------------------------------------------------



    return render_template(

        "register.html"

    )





# ============================================================

# LOGIN

# ============================================================



@app.route(

    "/login",

    methods=["GET", "POST"]

)

def login():



    if request.method == "POST":



        email = request.form.get(

            "email",

            ""

        ).strip().lower()



        password = request.form.get(

            "password",

            ""

        )





        if not email or not password:



            return render_template(

                "login.html",

                error="Please enter your email and password."

            )





        connection = get_connection()





        user = connection.execute(

            """

            SELECT *

            FROM users

            WHERE email = ?

            """,

            (email,)

        ).fetchone()





        connection.close()





        # ----------------------------------------------------

        # CHECK USER

        # ----------------------------------------------------



        if user:



            try:



                password_correct = check_password_hash(

                    user["password"],

                    password

                )



            except Exception:



                password_correct = False





            if password_correct:



                session["user_id"] = user["id"]



                session["user_name"] = user["name"]



                session["user_email"] = user["email"]





                return redirect(

                    url_for("dashboard")

                )





        # ----------------------------------------------------

        # INVALID LOGIN

        # ----------------------------------------------------



        return render_template(

            "login.html",

            error="Invalid email or password."

        )





    return render_template(

        "login.html"

    )





# ============================================================

# LOGOUT

# ============================================================



@app.route("/logout")

def logout():



    session.clear()



    return redirect(

        url_for("home")

    )





# ============================================================

# DASHBOARD

# ============================================================



@app.route("/dashboard")

def dashboard():



    if "user_id" not in session:



        return redirect(

            url_for("login")

        )





    connection = get_connection()





    interviews = connection.execute(

        """

        SELECT *

        FROM interviews

        WHERE user_id = ?

        ORDER BY id DESC

        """,

        (

            session["user_id"],

        )

    ).fetchall()





    connection.close()





    total_interviews = len(

        interviews

    )





    scores = [



        row["score"]



        for row in interviews



        if row["score"] is not None



    ]





    if scores:



        average_score = round(

            sum(scores) / len(scores)

        )



        best_score = round(

            max(scores)

        )



    else:



        average_score = 0



        best_score = 0





    recent_interviews = interviews[:5]





    return render_template(

        "dashboard.html",



        total_interviews=total_interviews,



        average_score=average_score,



        best_score=best_score,



        recent_interviews=recent_interviews,



        interviews=interviews

    )





# ============================================================

# START INTERVIEW

# ============================================================



@app.route(

    "/interview",

    methods=["GET", "POST"]

)

def interview():



    if "user_id" not in session:



        return redirect(

            url_for("login")

        )





    if request.method == "POST":



        role = request.form.get(

            "role",

            "Python Developer"

        ).strip()





        interview_type = request.form.get(

            "interview_type",

            "Technical"

        ).strip()





        difficulty = request.form.get(

            "difficulty",

            "Intermediate"

        ).strip()





        # ----------------------------------------------------

        # VALIDATE ROLE

        # ----------------------------------------------------



        if role not in QUESTIONS:



            role = "Python Developer"





        if not interview_type:



            interview_type = "Technical"





        if not difficulty:



            difficulty = "Intermediate"





        # ----------------------------------------------------

        # STORE INTERVIEW SETTINGS

        # ----------------------------------------------------



        session["interview_role"] = role



        session["interview_type"] = interview_type



        session["difficulty"] = difficulty



        session["question_index"] = 0





        # Clear previous answer



        session.pop(

            "current_question",

            None

        )



        session.pop(

            "current_answer",

            None

        )



        session.pop(

            "current_score",

            None

        )





        return redirect(

            url_for("question")

        )





    return render_template(

        "interview.html"

    )





# ============================================================

# QUESTION

# ============================================================



@app.route(

    "/question",

    methods=["GET", "POST"]

)

def question():



    if "user_id" not in session:



        return redirect(

            url_for("login")

        )





    role = session.get(

        "interview_role",

        "Python Developer"

    )





    questions = QUESTIONS.get(

        role,

        QUESTIONS["Python Developer"]

    )





    question_index = session.get(

        "question_index",

        0

    )





    # --------------------------------------------------------

    # ALL QUESTIONS COMPLETED

    # --------------------------------------------------------



    if question_index >= len(questions):



        return redirect(

            url_for("feedback")

        )





    current_question = questions[

        question_index

    ]





    total_questions = len(

        questions

    )





    current_number = (

        question_index + 1

    )





    progress = int(

        (

            current_number

            /

            total_questions

        )

        * 100

    )





    interview_type = session.get(

        "interview_type",

        "Technical"

    )





    time_limit = 120





    # --------------------------------------------------------

    # SUBMIT ANSWER

    # --------------------------------------------------------



    if request.method == "POST":



        answer = request.form.get(

            "answer",

            ""

        ).strip()





        if not answer:



            return render_template(

                "question.html",



                question=current_question,



                question_number=current_number,



                total_questions=total_questions,



                role=role,



                interview_type=interview_type,



                progress=progress,



                time_limit=time_limit,



                error="Please enter your answer before continuing."

            )





        # ----------------------------------------------------

        # CONTENT-BASED SCORE

        score = evaluate_answer(
            current_question,
            answer
        )


        # STORE CURRENT ANSWER

        # ----------------------------------------------------



        session["current_question"] = (

            current_question

        )



        session["current_answer"] = (

            answer

        )



        session["current_score"] = (

            score

        )





        # Move to next question



        session["question_index"] = (

            question_index + 1

        )





        return redirect(

            url_for("feedback")

        )





    # --------------------------------------------------------

    # DISPLAY QUESTION

    # --------------------------------------------------------



    return render_template(

        "question.html",



        question=current_question,



        question_number=current_number,



        total_questions=total_questions,



        role=role,



        interview_type=interview_type,



        progress=progress,



        time_limit=time_limit

    )





# ============================================================

# FEEDBACK

# ============================================================



@app.route("/feedback")
def feedback():

    if "user_id" not in session:
        return redirect(url_for("login"))

    score = int(session.get("current_score", 0))
    answer = session.get("current_answer", "No answer submitted.")
    question_text = session.get("current_question", "")
    role = session.get("interview_role", "Python Developer")
    interview_type = session.get("interview_type", "Technical")

    # --------------------------------------------------------
    # REALISTIC FEEDBACK BASED ON THE ACTUAL SCORE
    # --------------------------------------------------------

    if score == 0:
        performance_title = "Needs Improvement"
    elif score < 40:
        performance_title = "Weak Performance"
    elif score < 60:
        performance_title = "Fair Performance"
    elif score < 80:
        performance_title = "Good Performance"
    else:
        performance_title = "Excellent Performance"

    if score == 0:
        summary = (
            "Poor response. The answer did not contain enough relevant "
            "information to demonstrate understanding of the question."
        )
        strengths = [
            "You attempted the question."
        ]
        improvements = [
            "Answer the question directly instead of submitting an incomplete response.",
            "Include the important technical concepts related to the question.",
            "Explain your answer with a short example where appropriate."
        ]
        tip = (
            "Read the question carefully, identify the main concept, "
            "and explain it in 2–4 clear sentences."
        )
        relevance = "Poor"
        clarity = "Poor"
        confidence = "Poor"

    elif score < 40:
        summary = (
            "Weak response. You mentioned a relevant idea, but the answer "
            "needs more accurate explanation and supporting details."
        )
        strengths = [
            "Your answer contains at least one relevant concept."
        ]
        improvements = [
            "Explain the main concept more clearly.",
            "Include more of the important points asked in the question.",
            "Avoid very short or incomplete answers."
        ]
        tip = (
            "Start with a definition, then explain the concept and add a simple example."
        )
        relevance = "Fair"
        clarity = "Poor"
        confidence = "Fair"

    elif score < 60:
        summary = (
            "Fair response. You showed some understanding, but important "
            "technical details are still missing."
        )
        strengths = [
            "You included some relevant information.",
            "Your response shows partial understanding of the topic."
        ]
        improvements = [
            "Cover the key points more completely.",
            "Use technically precise terminology.",
            "Add an example to support your explanation."
        ]
        tip = (
            "Try to cover the definition, key differences or features, and one practical example."
        )
        relevance = "Fair"
        clarity = "Fair"
        confidence = "Fair"

    elif score < 80:
        summary = (
            "Good response. You demonstrated a reasonable understanding of "
            "the topic, but the explanation could be more complete and precise."
        )
        strengths = [
            "Your response addressed the main topic.",
            "You demonstrated a reasonable understanding of the concept."
        ]
        improvements = [
            "Add more technical detail where necessary.",
            "Include a practical example to strengthen the answer.",
            "Make the explanation more structured and precise."
        ]
        tip = (
            "Use the structure: definition → explanation → example → conclusion."
        )
        relevance = "Good"
        clarity = "Good"
        confidence = "Good"

    else:
        summary = (
            "Excellent response. You demonstrated strong understanding of "
            "the topic and covered the important concepts clearly."
        )
        strengths = [
            "Your response directly addressed the question.",
            "You demonstrated strong understanding of the concept.",
            "You included relevant technical information."
        ]
        improvements = [
            "Keep the explanation concise and well structured.",
            "Add a practical example when it can make the answer clearer.",
            "Continue using technically precise terminology."
        ]
        tip = (
            "Maintain the same structure and support important technical points with examples."
        )
        relevance = "Excellent"
        clarity = "Excellent"
        confidence = "Excellent"

    # --------------------------------------------------------
    # SAVE INTERVIEW RESULT
    # --------------------------------------------------------

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO interviews
        (
            user_id,
            role,
            interview_type,
            score,
            date,
            question,
            answer,
            feedback
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            role,
            interview_type,
            score,
            datetime.now().strftime("%d %b %Y"),
            question_text,
            answer,
            summary
        )
    )

    connection.commit()
    connection.close()

    return render_template(
        "feedback.html",
        score=score,
        answer=answer,
        summary=summary,
        strengths=strengths,
        improvements=improvements,
        tip=tip,
        relevance=relevance,
        clarity=clarity,
        confidence=confidence,
        performance_title=performance_title
    )


# ============================================================

# HISTORY

# ============================================================



@app.route("/history")

def history():



    if "user_id" not in session:



        return redirect(

            url_for("login")

        )





    connection = get_connection()





    history_data = connection.execute(

        """

        SELECT *

        FROM interviews

        WHERE user_id = ?

        ORDER BY id DESC

        """,

        (

            session["user_id"],

        )

    ).fetchall()





    connection.close()





    total_interviews = len(

        history_data

    )





    scores = [



        row["score"]



        for row in history_data



        if row["score"] is not None



    ]





    if scores:



        average_score = round(

            sum(scores) / len(scores)

        )



        best_score = round(

            max(scores)

        )



    else:



        average_score = 0



        best_score = 0





    improvement = 0





    if len(scores) >= 2:



        improvement = round(

            scores[0] - scores[-1]

        )





    return render_template(

        "history.html",



        history=history_data,



        total_interviews=total_interviews,



        average_score=average_score,



        best_score=best_score,



        improvement=improvement

    )





# ============================================================

# RUN APPLICATION

# ============================================================



if __name__ == "__main__":



    app.run(

        debug=True

    )