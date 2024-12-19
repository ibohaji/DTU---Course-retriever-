from flask import Flask, render_template, request, jsonify
import os
from ColBERTv2 import search
from ragatouille import RAGPretrainedModel

# Get the absolute path to the frontend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, 'course_retriever', 'frontend')

app = Flask(__name__, 
    static_folder=frontend_dir,
    static_url_path='',
    template_folder=frontend_dir
)

# Initialize the RAG model globally
INDEX_PATH = "ColBERTv2/.ragatouille/colbert/indexes/DTU Course-base"
RAG = RAGPretrainedModel.from_index(INDEX_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_endpoint():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    results_per_page = 10  # Number of results per page
    
    if not query:
        return '<div class="no-results">Please enter a search query</div>'
    
    # Get all results using RAG model
    all_results = search(RAG, query)
    
    # Paginate results
    start_idx = (page - 1) * results_per_page
    end_idx = start_idx + results_per_page
    paginated_results = all_results[start_idx:end_idx]
    
    # Only render results if we have them
    if paginated_results:
        return render_template('_results.html', 
                            results=paginated_results,
                            query=query,
                            page=page)
    elif page == 1:
        return '<div class="no-results">No courses found matching your search.</div>'
    else:
        return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)