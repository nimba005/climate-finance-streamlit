import PyPDF2
import matplotlib.pyplot as plt

# === Step 1: Extract text from PDF ===
def extract_text_from_pdf(filename):
    with open(filename, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# === Step 2: Dummy text analysis (replace with NLP/LLM later) ===
def analyze_text(text):
    # For demo: we’ll just fake percentages
    indicators = {
        "Total Public Investment in Climate Initiatives": 2000000,
        "Percentage of National Budget Allocated to Climate Adaptation": 5,
        "Year-on-Year Budget Increase for Climate Adaptation": 7,
        "Private Sector Investment Mobilized": 500000,
        "Funding Allocation by Sector": {
            "Energy": 30,
            "Agriculture": 25,
            "Health": 20,
            "Transport": 15,
            "Water": 10
        }
    }
    return indicators

# === Step 3: Display Results ===
def display_results(indicators):
    print("\n=== Climate Finance Indicators ===")
    for k, v in indicators.items():
        if isinstance(v, dict):
            print(f"\n{k}:")
            for sector, pct in v.items():
                print(f"  {sector}: {pct}%")
        else:
            print(f"{k}: {v}")

    # Graph: Funding Allocation by Sector
    sectors = list(indicators["Funding Allocation by Sector"].keys())
    values = list(indicators["Funding Allocation by Sector"].values())

    plt.figure(figsize=(6,6))
    plt.pie(values, labels=sectors, autopct='%1.1f%%')
    plt.title("Funding Allocation by Sector")
    plt.show()

# === Step 4: Main program ===
if __name__ == "__main__":
    filename = input("Enter PDF filename (e.g., budget.pdf): ")
    text = extract_text_from_pdf(filename)
    results = analyze_text(text)
    display_results(results)