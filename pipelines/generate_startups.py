"""
generate_startups.py
────────────────────
Generates a realistic startup ecosystem dataset for UVU Africa's
innovation portfolio. In production this would pull from:
  - Disrupt Africa API / scrape
  - Crunchbase public data
  - StartupBlink

For now it produces a rich, reproducible mock dataset that can be
swapped for real data once API access is obtained.

Outputs:
  data/startups.csv

Usage:
    python pipelines/generate_startups.py
"""

import pandas as pd
import random
import os
import logging

# ── Configuration ─────────────────────────────────────────────────────────────

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "startups.csv")
RANDOM_SEED = 42

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Reference Data ────────────────────────────────────────────────────────────

SECTORS = [
    "FinTech", "EdTech", "AI/ML", "HealthTech",
    "Biotechnology", "CleanTech", "AgriTech", "Cybersecurity",
]

COUNTRIES = [
    "South Africa", "Kenya", "Nigeria", "Rwanda",
    "Ghana", "Tanzania", "Uganda", "Ethiopia",
]

STATUSES = ["Active", "Active", "Active", "Scaling", "Early Stage", "Acquired", "Closed"]

PROGRAM_IDS = list(range(1, 11))

CITIES = {
    "South Africa": ["Cape Town", "Johannesburg", "Durban", "Gqeberha", "Pretoria"],
    "Kenya":        ["Nairobi", "Mombasa"],
    "Nigeria":      ["Lagos", "Abuja", "Port Harcourt"],
    "Rwanda":       ["Kigali"],
    "Ghana":        ["Accra", "Kumasi"],
    "Tanzania":     ["Dar es Salaam", "Dodoma"],
    "Uganda":       ["Kampala"],
    "Ethiopia":     ["Addis Ababa"],
}

STARTUP_NAMES = [
    "PayBright","LearnLoop","DataSense","MedTrack","BioNova","SolarStream","FarmIQ","ShieldNet",
    "CapiPay","EduPath","Neuro AI","HealthHub","GenomicsZA","GreenGrid","CropCast","CyberAfrica",
    "MobiBank","ClassCloud","VisionAI","CareConnect","BioSpark","WindWave","RootAI","LockChain",
    "SwiftCash","SkillBridge","DeepData","NurseTech","LabSync","SunPower","PrecisionFarm","SafeID",
    "FlexPay","OpenEdu","AIHarvest","ClinixAI","CellTech","EcoCharge","AgriSense","NetGuard",
    "WalletX","TutorBot","SmartVision","HealthIQ","BioMatrix","BluEnergy","FieldBot","TrustLayer",
    "QuickFunds","CourseAI","DataFarm","MedBot","NanoLab","ChargeSA","SoilSense","AuthShield",
    "CreditLink","LearnAI","AgroTrack","PharmaBot","PeptideCo","SolarBee","HarvestIQ","SecurePay",
    "TransferGo","EduCloud","CropMind","ClinicNet","CellVault","WindCore","FarmData","CipherNet",
    "LoanTech","StudyAI","VisionFarm","PatientAI","BioVault","GridSense","PlantIQ","DataShield",
    "MicroPay","KnowledgeBase","IrrigAI","WellnessAI","LabCore","EcoTech","SeedBot","GuardAI",
    "RemitPro","TalentAI","PrecisionGrow","HealthStream","ChemSpark","SunGrid","AgroBot","NetSafe",
    "PocketBank","SmartLearn","FieldSense","MedChain","GeneLab","PowerGrid","HarvestBot","CyberSafe",
    "ZapPay","CampusAI",
]

# ── Generator ─────────────────────────────────────────────────────────────────

def generate_startups(seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Generate a realistic startup DataFrame."""
    random.seed(seed)
    rows = []

    for i, name in enumerate(STARTUP_NAMES):
        country = random.choice(COUNTRIES)
        sector  = SECTORS[i % len(SECTORS)]
        year    = random.randint(2012, 2024)
        status  = random.choice(STATUSES)

        # Funding logic: older + scaling startups raise more
        base_funding = random.randint(30_000, 500_000)
        multiplier   = 1.0
        if status == "Scaling":
            multiplier = random.uniform(3.0, 10.0)
        elif status == "Acquired":
            multiplier = random.uniform(5.0, 20.0)
        elif year < 2018:
            multiplier = random.uniform(1.5, 5.0)

        funding = int(base_funding * multiplier)

        rows.append({
            "startup_id":   i + 1,
            "startup_name": name,
            "sector":       sector,
            "country":      country,
            "city":         random.choice(CITIES[country]),
            "founded_year": year,
            "funding_usd":  funding,
            "program_id":   random.choice(PROGRAM_IDS),
            "status":       status,
            "employees":    random.randint(2, 150),
            "revenue_usd":  int(funding * random.uniform(0.1, 0.8)),
        })

    df = pd.DataFrame(rows)
    return df


# ── Validation ────────────────────────────────────────────────────────────────

def validate(df: pd.DataFrame) -> bool:
    """Basic data quality checks."""
    checks = {
        "No null startup names": df["startup_name"].isnull().sum() == 0,
        "No negative funding":   (df["funding_usd"] >= 0).all(),
        "Valid founded years":    df["founded_year"].between(2000, 2025).all(),
        "Known sectors only":     df["sector"].isin(SECTORS).all(),
    }
    all_passed = True
    for check, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        log.info(f"  [{status}] {check}")
        if not passed:
            all_passed = False
    return all_passed


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log.info("Generating startup ecosystem dataset ...")
    df = generate_startups()

    log.info("Running data validation ...")
    valid = validate(df)

    if not valid:
        log.error("Validation failed. Please review the data before saving.")
        return

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

    log.info(f"startups.csv saved: {len(df)} rows, {len(df.columns)} columns")
    log.info(f"Saved to: {os.path.abspath(DATA_PATH)}")

    # Quick summary
    log.info("\n── Dataset Summary ──────────────────────────────")
    log.info(f"  Total startups:    {len(df)}")
    log.info(f"  Sectors covered:   {df['sector'].nunique()}")
    log.info(f"  Countries covered: {df['country'].nunique()}")
    log.info(f"  Total funding:     ${df['funding_usd'].sum():,.0f}")
    log.info(f"  Avg funding:       ${df['funding_usd'].mean():,.0f}")
    log.info(f"  Active startups:   {(df['status'] == 'Active').sum()}")


if __name__ == "__main__":
    main()