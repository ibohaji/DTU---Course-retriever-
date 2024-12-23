from ragatouille import RAGPretrainedModel
import os
from infra.db.course_db import CourseDB
import warnings



warnings.filterwarnings("ignore")

class ColBERTv2Searcher:
    def __init__(self):
        # Get the absolute path to the index
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        index_path = os.path.join(current_dir, "retrieval/ColBERTv2/.ragatouille/colbert/indexes/DTU Course-base")
        self.model = RAGPretrainedModel.from_index(index_path)


    def search(self, query: str, k: int = 100) -> list[dict]:
        # Get initial results
        results = self.model.search(query, k=k)
        
        # Filter out duplicates, keeping highest scoring version
        filtered_results = self._filter_results(results)
        
        # Convert to structured course objects
        structured_results = self.structured_results(filtered_results)
        
        # Sort by search rank to ensure proper ordering
        structured_results.sort(key=lambda x: x["search_rank"], reverse=True)
        
        return structured_results
        




    def structured_results(self, results: list[dict]) -> list[dict]:
        course_db = CourseDB()
        courses = [] 

        for result in results: 
            course_number = result["document_metadata"]["course_number"]
            course = course_db.get_course(course_number)
            
            # Add search rank from the search results
            course["search_rank"] = float(result["score"])
            
            # Check for required fields and log if missing
            required_fields = [
                "course_url", "details", 
                "general_course_objectives", "learning_objectives", "content"
            ]
            
            missing_fields = [field for field in required_fields if field not in course]
            if missing_fields:
                print(f"Warning: Course {course_number} is missing required fields: {missing_fields}")
            
            courses.append(course)
        
        return courses


    def _filter_results(self, results: list[dict]) -> list[dict]:
        # Keep track of best score for each course
        best_results = {}
        
        for result in results:
            course_number = result["document_metadata"]["course_number"]
            current_score = result["score"]
            
            # Either add new course or update if better score found
            if (course_number not in best_results or 
                current_score > best_results[course_number]["score"]):
                result["document_id"] = course_number
                best_results[course_number] = result
        
        return list(best_results.values())

    def rerank(self, results: list[dict]) -> list[dict]:
        # Compute the sum of scores for each chunk
        score_keeper = {}
        for result in results:
            course_number = result["document_id"]
            if course_number not in score_keeper:
                score_keeper[course_number] = 0
            score_keeper[course_number] += result["score"]

        top_course_numbers = sorted(score_keeper.items(), key=lambda x: x[1], reverse=True)
        
        filtered_results = []
        for course_number, _ in top_course_numbers:
            for result in results:
                if result["document_id"] == course_number:
                    result["score"] = score_keeper[course_number]
                    filtered_results.append(result)
                    break
        
        return filtered_results


if __name__ == "__main__":
    searcher = ColBERTv2Searcher()
    results = searcher.search("Machine learning theory?")
    print(f"Top {len(results)} results:")
    for result in results:
        print(f"result score: {result['score']}\nresult document_metadata: {result['document_metadata']}")