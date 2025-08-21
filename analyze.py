import PyPDF2
import matplotlib.pyplot as plt
import re

# === Step 1: Extract text from PDF ===
def extract_text_from_pdf(filename):
    with open(filename, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# === Step 2: Analyze numbers from text ===
def analyze_text(text):
    indicators = {
        "Total Public Investment in Climate Initiatives": 0,
        "Percentage of National Budget Allocated to Climate Adaptation": 0,
        "Year-on-Year Budget Increase for Climate Adaptation": 0,
        "Private Sector Investment Mobilized": 0,
        "Funding Allocation by Sector": {
            "Energy": 0,
            "Agriculture": 0,
            "Health": 0,
            "Transport": 0,
            "Water": 0
        }
    }

    # Example regex-based parsing (improve depending on your PDF)
    total_match = re.search(r"Total\s+Public\s+Investment.*?([\d,]+)", text, re.IGNORECASE)
    if total_match:
        indicators["Total Public Investment in Climate Initiatives"] = int(total_match.group(1).replace(",", ""))

    pct_match = re.search(r"Climate\s+Adaptation\s*:\s*(\d+)%", text, re.IGNORECASE)
    if pct_match:
        indicators["Percentage of National Budget Allocated to Climate Adaptation"] = int(pct_match.group(1))

    yoy_match = re.search(r"Year.?on.?Year.*?(\d+)%", text, re.IGNORECASE)
    if yoy_match:
        indicators["Year-on-Year Budget Increase for Climate Adaptation"] = int(yoy_match.group(1))

    private_match = re.search(r"Private\s+Sector\s+Investment.*?([\d,]+)", text, re.IGNORECASE)
    if private_match:
        indicators["Private Sector Investment Mobilized"] = int(private_match.group(1).replace(",", ""))

    # Sector breakdown example
    for sector in indicators["Funding Allocation by Sector"].keys():
        match = re.search(rf"{sector}.*?(\d+)%", text, re.IGNORECASE)
        if match:
            indicators["Funding Allocation by Sector"][sector] = int(match.group(1))

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

    if sum(values) > 0:   # ✅ Prevents the NaN error
        plt.figure(figsize=(6,6))
        plt.pie(values, labels=sectors, autopct='%1.1f%%')
        plt.title("Funding Allocation by Sector")
        plt.show()
    else:
        print("\n⚠️ No sector data found, skipping chart.")

# === Step 4: Main program ===
if __name__ == "__main__":
    filename = input("Enter PDF filename (e.g., budget.pdf): ")
    text = extract_text_from_pdf(filename)
    results = analyze_text(text)
    display_results(results)
