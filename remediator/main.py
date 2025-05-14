import json, subprocess
from typing import List, Dict

def load_plan(path="tfplan.binary"):
    subprocess.run(["terraform", "show", "-json", path], check=True, stdout=open("plan.json","w"))
    return json.load(open("plan.json"))

def evaluate(plan_json_path: str = "../plan.json") -> List[Dict]:
    """
    Run OPA against the given Terraform plan JSON and return a list of violation messages.
    """
    # Build the CLI command
    cmd = [
        "opa", "eval",
        "--data", "policies/",           # your policies folder
        "--input", plan_json_path,       # path to the tfplan JSON
        "--format", "json",              # JSON output
        "data.terraform.deny[]"          # query: every element in deny[]
    ]

    try:
        raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # OPA returns exit code 2 if there are no matches, so we still want to parse output
        raw = e.output

    # Parse the JSON result
    result = json.loads(raw)

    # OPA JSON shape:
    # {
    #   "result": [
    #     { "expressions": [ { "value": "<your msg>" } ], ... },
    #     ...
    #   ]
    # }
    violations = []
    for expr in result.get("result", []):
        # each expr["expressions"] is a list; we took deny[] so there’s one value
        msg = expr["expressions"][0]["value"]
        violations.append({"message": msg})
    return violations

def remediate(violations: List[Dict]):
    for v in violations:
        # simple example: target the offending resource
        addr = extract_address_from(v["message"])
        subprocess.run(["terraform", "apply", "-target", addr, "-auto-approve"])

if __name__ == "__main__":
    viols = evaluate()
    if viols:
        print("Found violations:")
        for v in viols:
            print(" •", v["message"])
    else:
        print("No policy violations detected.")
