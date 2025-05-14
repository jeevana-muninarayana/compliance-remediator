name: Compliance CI

on:
  pull_request:
    branches: [develop, main]

jobs:
  test-and-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.4.0

      - name: Init & Plan
        run: |
          cd infra/
          terraform init
          terraform plan -out=tfplan.binary

      - name: Scan with OPA
        run: |
          opa test policies/
          opa eval --data policies/ --input infra/plan.json 'data.terraform.deny'
        
      - name: Run Remediator
        if: always()
        run: |
          cd remediator/
          pip install -r requirements.txt
          python main.py
