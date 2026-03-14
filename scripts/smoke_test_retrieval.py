import requests
import json
import time

def run_smoke_test():
    url = "http://127.0.0.1:8000/rag/search"
    
    # Test queries based on typical "mini-llm-twin" content
    test_queries = [
        "What is the core architecture of this project?",
        "How do I use MongoDB Atlas for vector search?",
        "Explain the chunking strategy",
        "", # Test empty query (should return [] or 422 depending on implementation)
    ]
    
    print("Starting Phase 3 Smoke Test...\n")
    
    for query in test_queries:
        payload = {
            "query": query,
            "top_k": 3
        }
        
        print(f"Testing Query: '{query or 'EMPTY_STRING'}'")
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                print(f"Status: 200 | Latency: {latency:.2f}s | Results Found: {len(results)}")
                
                if results:
                    print(f"   Top Score: {results[0].get('score'):.4f}")
                    print(f"   Sample Text: {results[0].get('text')[:70]}...")
            elif response.status_code == 422:
                print(f"Status: 422 (Correctly rejected invalid input)")
            else:
                print(f" Status: {response.status_code} | Error: {response.text}")
                
        except Exception as e:
            print(f"Server unreachable. Did you start the FastAPI server?\nError: {e}")
            break
            
        print("-" * 30)

if __name__ == "__main__":
    run_smoke_test()
