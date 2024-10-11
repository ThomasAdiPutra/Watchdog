from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from concurrent.futures import ProcessPoolExecutor, as_completed

def check(hypothesis, threshold = 0, method = 'cosine', max_result = None, order = 'DESC'):
    hypothesis = preprocess_text(hypothesis)

    method = method.lower()
    order = order.upper()

    references = list_of_references()
    results = []

    with ProcessPoolExecutor() as executor:
        future_to_reference = {
            executor.submit(
                calculate_bleu_score if method == 'bleu' else calculate_cosine_similarity,
                preprocess_text(read_reference_file(reference)),
                hypothesis
            ): reference
            for reference in references
        }

        for future in as_completed(future_to_reference):
            reference = future_to_reference[future]
            try:
                score = future.result()
                results.append({
                    "score": score.round(5),
                    "source": reference['path'] + '/' + reference['filename'],
                })
            except Exception as e:
                print(f"Error calculating similarity for '{reference['filename']}': {e}")

    # Filter results by threshold and sort
    results = [result for result in results if result['score'] >= threshold]
    results.sort(key=lambda x: x['score'], reverse=order == 'DESC')
    results = results[:int(max_result)] if max_result else results

    return results

def list_of_references(folder='dataset'):
    references = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            references.append({
                'path': root,
                'filename': filename,
            })
    return references

def read_reference_file(reference):
    with open(os.path.join(reference['path'], reference['filename']), 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def preprocess_text(text):
    return ' '.join(text.split()).lower()

def calculate_cosine_similarity(reference, hypothesis):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([reference, hypothesis])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return cosine_sim

def calculate_bleu_score(reference, hypothesis):
    n_gram_order = 3
    smoothing_function = SmoothingFunction().method1  # Menggunakan metode smoothing
    bleu_score = sentence_bleu([reference], hypothesis, weights=(1 / n_gram_order,) * n_gram_order, smoothing_function=smoothing_function)
    return bleu_score