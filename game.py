from flask import Flask, render_template, request, Response, session
import base64
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

COMMON_STYLES = """
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .challenge-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .hint {
        color: #666;
        display: none;
        background: #f8f9fa;
        padding: 15px;
        border-left: 4px solid #007bff;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
    .hint-btn {
        cursor: pointer;
        color: #007bff;
        text-decoration: none;
        display: inline-block;
        margin: 10px 0;
        padding: 5px 10px;
        border: 1px solid #007bff;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .hint-btn:hover {
        background: #007bff;
        color: white;
    }
    .code-form {
        margin: 20px 0;
        text-align: center;
    }
    .code-input {
        padding: 10px;
        width: 250px;
        border: 2px solid #ddd;
        border-radius: 5px;
        margin-right: 10px;
        font-size: 16px;
    }
    button {
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        transition: background 0.3s ease;
    }
    button:hover {
        background: #0056b3;
    }
    .top-progress {
        position: sticky;
        top: 0;
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        z-index: 100;
    }
    .progress-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .progress-stats {
        font-size: 14px;
        color: #666;
    }
    .progress-bar {
        width: 100%;
        height: 10px;
        background: #eee;
        border-radius: 5px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        transition: width 0.5s ease;
    }
    .challenge-badges {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 10px;
    }
    .badge {
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .badge.complete {
        background: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #a5d6a7;
    }
    .badge.incomplete {
        background: #fff3e0;
        color: #ef6c00;
        border: 1px solid #ffe0b2;
    }
    .success-message {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        margin: 20px 0;
    }
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        margin: 20px 0;
    }
</style>
"""

def get_progress_bar(current_challenge=None):
    completed = sum(session['progress'].values())
    total = len(session['progress'])
    progress_percent = (completed / total) * 100
    
    challenges_status = ""
    for i in range(1, total + 1):
        challenge_key = f'challenge{i}'
        is_complete = session['progress'][challenge_key]
        is_current = current_challenge and current_challenge == i
        
        status_class = 'complete' if is_complete else 'incomplete'
        icon = '✅' if is_complete else '⏳'
        
        challenges_status += f"""
        <div class="badge {status_class}">
            {icon} Challenge {i}
        </div>
        """

    return f"""
    <div class="top-progress">
        <div class="progress-container">
            <div class="progress-stats">
                Progress: {completed}/{total} Challenges Complete
            </div>
            <div class="progress-stats">
                {progress_percent:.0f}% Complete
            </div>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_percent}%"></div>
        </div>
        <div class="challenge-badges">
            {challenges_status}
        </div>
    </div>
    """

@app.before_request
def initialize_progress():
    if 'progress' not in session:
        session['progress'] = {'challenge1': False, 'challenge2': False, 'challenge3': False}

@app.route("/")
def home():
    session['progress'] = {'challenge1': False, 'challenge2': False, 'challenge3': False}
    return f"""
    {COMMON_STYLES}
    {get_progress_bar()}
    <div class="challenge-card">
        <h1>Welcome to the Web Scraping Adventure! 🗺️</h1>
        <p>Embark on a journey to find hidden treasures using your web scraping skills!</p>
        <p>Rules:</p>
        <ul>
            <li>Each challenge requires different web scraping techniques</li>
            <li>Find the secret code in each challenge to progress</li>
            <li>Use tools like 'View Page Source' and your browser's developer tools</li>
            <li>Need help? Click the hint buttons!</li>
        </ul>
        <div style="text-align: center; margin-top: 20px;">
            <a href="/challenge1" style="text-decoration: none;">
                <button>Start Adventure!</button>
            </a>
        </div>
    </div>
    <script type="text/javascript">
        function toggleHint(id) {
            const hint = document.getElementById(id);
            hint.style.display = hint.style.display === 'none' ? 'block' : 'none';
        }
    </script>
    """

@app.route("/challenge1", methods=['GET', 'POST'])
def challenge1():
    if request.method == 'POST':
        if request.form.get('code') == 'PYTHON_EXPLORER_2024':
            session['progress']['challenge1'] = True
            return f"""
            {COMMON_STYLES}
            {get_progress_bar(1)}
            <div class="challenge-card">
                <div class="success-message">
                    <h2>✅ Challenge 1 Complete!</h2>
                    <p>Moving to Challenge 2...</p>
                </div>
            </div>
            <script>setTimeout(() => window.location.href = '/challenge2', 2000)</script>
            """
        return f"""
        {COMMON_STYLES}
        {get_progress_bar(1)}
        <div class="challenge-card">
            <div class="error-message">❌ Incorrect code. Try again!</div>
            <a href="/challenge1">Back to Challenge 1</a>
        </div>
        """

    return f"""
    {COMMON_STYLES}
    {get_progress_bar(1)}
    <div class="challenge-card">
        <h1>Challenge 1: Hidden in Plain Sight 👀</h1>
        <!-- Secret Code: PYTHON_EXPLORER_2024 -->
        <p>Find the secret code hidden in this page's source code!</p>
        
        <div class="hint-btn" onclick="toggleHint('hint1')">🔍 Need a hint?</div>
        <p id="hint1" class="hint">
            Hint 1: Right-click on the page and select "View Page Source"<br>
            Hint 2: Look for HTML comments (they start with &lt;!-- and end with --&gt;)
        </p>

        <form class="code-form" method="POST">
            <input type="text" name="code" class="code-input" placeholder="Enter the secret code">
            <button type="submit">Submit</button>
        </form>
    </div>
    """

@app.route("/challenge2", methods=['GET', 'POST'])
def challenge2():
    if request.method == 'POST':
        if request.form.get('code') == 'HEADER_HUNTER_42':
            session['progress']['challenge2'] = True
            return f"""
            {COMMON_STYLES}
            {get_progress_bar(2)}
            <div class="challenge-card">
                <div class="success-message">
                    <h2>✅ Challenge 2 Complete!</h2>
                    <p>Moving to Challenge 3...</p>
                </div>
            </div>
            <script>setTimeout(() => window.location.href = '/challenge3', 2000)</script>
            """
        return f"""
        {COMMON_STYLES}
        {get_progress_bar(2)}
        <div class="challenge-card">
            <div class="error-message">❌ Incorrect code. Try again!</div>
            <a href="/challenge2">Back to Challenge 2</a>
        </div>
        """

    response = Response(f"""
    {COMMON_STYLES}
    {get_progress_bar(2)}
    <div class="challenge-card">
        <h1>Challenge 2: Headers and Metadata 🔍</h1>
        <p>The secret code is hidden in the response headers!</p>
        
        <div class="hint-btn" onclick="toggleHint('hint2')">🔍 Need a hint?</div>
        <p id="hint2" class="hint">
            Hint 1: Open Developer Tools (F12 or right-click -> Inspect)<br>
            Hint 2: Go to the Network tab and refresh the page<br>
            Hint 3: Look for a header starting with 'X-Secret'
        </p>

        <form class="code-form" method="POST">
            <input type="text" name="code" class="code-input" placeholder="Enter the secret code">
            <button type="submit">Submit</button>
        </form>
    </div>
    """)
    response.headers['X-Secret-Code'] = 'HEADER_HUNTER_42'
    return response

@app.route("/challenge3", methods=['GET', 'POST'])
def challenge3():
    if request.method == 'POST':
        if request.form.get('code') == 'MASTER_SCRAPER_99':
            session['progress']['challenge3'] = True
            return f"""
            {COMMON_STYLES}
            {get_progress_bar(3)}
            <div class="challenge-card">
                <div class="success-message">
                    <h2>✅ Challenge 3 Complete!</h2>
                    <p>Moving to Victory...</p>
                </div>
            </div>
            <script>setTimeout(() => window.location.href = '/victory', 2000)</script>
            """
        return f"""
        {COMMON_STYLES}
        {get_progress_bar(3)}
        <div class="challenge-card">
            <div class="error-message">❌ Incorrect code. Try again!</div>
            <a href="/challenge3">Back to Challenge 3</a>
        </div>
        """

    secret_message = base64.b64encode("MASTER_SCRAPER_99".encode()).decode()
    return f"""
    {COMMON_STYLES}
    {get_progress_bar(3)}
    <div class="challenge-card">
        <h1>Challenge 3: Encoding Secrets 🔐</h1>
        <p>This secret code is encoded in base64. Decode it to proceed!</p>
        <div class="secret" data-encoded="{secret_message}"></div>
        
        <div class="hint-btn" onclick="toggleHint('hint3')">🔍 Need a hint?</div>
        <p id="hint3" class="hint">
            Hint 1: Find the encoded data in the div's 'data-encoded' attribute<br>
            Hint 2: Use an online base64 decoder<br>
            Hint 3: The encoded value is: {secret_message}
        </p>

        <form class="code-form" method="POST">
            <input type="text" name="code" class="code-input" placeholder="Enter the decoded secret">
            <button type="submit">Submit</button>
        </form>
    </div>
    """

@app.route("/victory")
def victory():
    if not all(session['progress'].values()):
        return f"""
        {COMMON_STYLES}
        {get_progress_bar()}
        <div class="challenge-card">
            <div class="error-message">
                🚫 Nice try! But you need to complete all challenges first!
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/" style="text-decoration: none;">
                    <button>Start Over</button>
                </a>
            </div>
        </div>
        """
    
    return f"""
    {COMMON_STYLES}
    {get_progress_bar()}
    <div class="challenge-card">
        <h1>🎉 Congratulations, Web Scraping Master! 🎉</h1>
        <p>You've successfully completed all challenges and demonstrated these web scraping skills:</p>
        <ul>
            <li>✅ Finding hidden HTML comments</li>
            <li>✅ Inspecting HTTP headers</li>
            <li>✅ Decoding base64 encoded content</li>
        </ul>
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" style="text-decoration: none;">
                <button>Start Over</button>
            </a>
        </div>
    </div>
    """

if __name__ == "__main__":
    app.run(debug=True)
