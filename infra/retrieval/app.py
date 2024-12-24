from flask import Flask, render_template, request
from infra.app.users import  StudentDependencies, get_result_agent, study_plan_agent
from infra.retrieval.ColBERTv2.searcher import ColBERTv2Searcher
from datetime import datetime
from pathlib import Path

# Get the absolute path to the UI directory
UI_DIR = Path(__file__).parent.parent.parent / 'UI'

app = Flask(__name__, 
    static_folder=str(UI_DIR / 'templates/static'),
    template_folder=str(UI_DIR / 'templates')
)
print(app.static_folder)
print(app.template_folder)

searcher = ColBERTv2Searcher()
deps = StudentDependencies(rag_retriever=searcher)

@app.route('/')
def index():
    return render_template('base.html')


@app.route('/chat/user', methods=['POST'])
async def chat_user():
    user_message = request.form.get('message', '')
    print(f"Received user message: {user_message}")
    return render_template('components/message.html',
        message=user_message,
        is_user=True,
        timestamp=datetime.now().strftime("%I:%M %p")
    )

@app.route('/chat/ai', methods=['POST'])
async def chat_ai():
    user_message = request.form.get('message', '')
    result = await get_result_agent(user_message, deps)
    return render_template('components/message.html',
        message=result.data.recommendations + "\n\n" + result.data.detailed_explanation + "\n\n" + result.data.gaps,
        is_user=False,
        timestamp=datetime.now().strftime("%I:%M %p")
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)