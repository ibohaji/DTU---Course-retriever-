from ragatouille import RAGPretrainedModel

def search(model, query, k = 40):
    results = model.search(query, k = k)
    return filter_results(results)



def filter_results(results:list[dict])->list[dict]:
    # Filter out results that belong to the same course 
    # Change document_id to course_number 
    seen_courses = []
    filtered_results = []
    for result in results: 
        course_number = result["document_metadata"]["course_number"]
        if course_number not in seen_courses:
            result["document_id"] = course_number
            seen_courses.append(course_number)
            filtered_results.append(result)
        else:
            if filtered_results[seen_courses.index(course_number)]["score"] < result["score"]:
                filtered_results[seen_courses.index(course_number)]["score"] = result["score"] 
                filtered_results[seen_courses.index(course_number)]["document_id"] = course_number

    return filtered_results

def rerank(results): 
    # Compute the sum of scores for each chunk
    score_keeper = {}
    for result in results:
        course_number = result["document_id"]
        if course_number not in score_keeper:
            score_keeper[course_number] = 0
        score_keeper[course_number] += result["score"]

    # TODO: Make this safe,
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
    results = search("Machine learning theory?", ".ragatouille/colbert/indexes/DTU Course-base")
    print(f"Top {len(results)} results:")
    for result in results:
        print(f"result score: {result['score']}\nresult document_metadata: {result['document_metadata']}")
