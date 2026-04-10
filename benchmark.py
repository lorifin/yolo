import json
from classifier import simple_classifier

def run_benchmark():
    with open('formation/banque_tests.json', 'r') as f:
        tests = json.load(f)
    reussites = 0
    for t in tests:
        pred = simple_classifier(t['phrase'])
        if t['attendu'] in pred: reussites += 1
    
    precision = (reussites / len(tests)) * 100
    with open('formation/data.js', 'w') as f:
        f.write(f"const accuracyScore = {precision};\n")
    print(f"Benchmark terminé : {precision}% de précision.")

if __name__ == "__main__":
    run_benchmark()
