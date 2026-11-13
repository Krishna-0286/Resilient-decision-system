import json

class RulesEngine:
    def __init__(self, config_path: str = "config.json"):
        # Load the business rules from the JSON file when the engine starts
        with open(config_path, "r") as file:
            self.config = json.load(file)
        self.rules = self.config.get("rules", {})

    def evaluate(self, application_data: dict):
        """
        Evaluates the data against the rules and generates a decision and a trace.
        """
        trace = [] # This will be our audit trail

        # 1. Mandatory Check
        if self.rules["mandatory_checks"]["requires_documents"]:
            if not application_data.get("documents_provided"):
                trace.append("Failed mandatory check: documents were not provided.")
                return "REJECTED", trace
            trace.append("Passed mandatory check: documents provided.")

        # 2. Threshold Check
        min_income = self.rules["threshold_checks"]["min_income"]
        if application_data.get("income", 0) < min_income:
            trace.append(f"Failed threshold check: income is below {min_income}.")
            return "REJECTED", trace
        trace.append(f"Passed threshold check: income is >= {min_income}.")

        # 3. Conditional Branching
        review_age = self.rules["conditional_branching"]["manual_review_age"]
        if application_data.get("age", 0) >= review_age:
            trace.append(f"Conditional trigger: Applicant age is {application_data['age']} (>= {review_age}).")
            return "MANUAL_REVIEW", trace

        # If everything passes and no special conditions are met
        trace.append("All rules passed successfully.")
        return "APPROVED", trace