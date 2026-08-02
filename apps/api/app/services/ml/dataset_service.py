import json
import os
import random
from typing import Any


class MLDatasetGenerator:
    """Dataset Generator for HR, CRM, Finance, Inventory, Manufacturing, Sales, Customers, Suppliers."""

    @staticmethod
    def generate_hr_attrition_dataset(records: int = 100) -> list[dict[str, Any]]:
        departments = [
            "Engineering",
            "Sales",
            "Marketing",
            "HR",
            "Finance",
            "Operations",
        ]
        data = []
        for i in range(1, records + 1):
            sat = round(random.uniform(1.5, 5.0), 1)
            overtime = random.randint(0, 30)
            tenure = random.randint(6, 72)
            sal_pct = random.randint(20, 95)
            attrition = (
                1
                if (sat < 2.5 and overtime > 15) or (sal_pct < 30 and overtime > 20)
                else 0
            )

            data.append(
                {
                    "employee_id": f"EMP-{1000 + i}",
                    "department": random.choice(departments),
                    "tenure_months": tenure,
                    "satisfaction_score": sat,
                    "overtime_hours": overtime,
                    "salary_percentile": sal_pct,
                    "attrition_flag": attrition,
                }
            )
        return data

    @staticmethod
    def generate_crm_churn_dataset(records: int = 100) -> list[dict[str, Any]]:
        tiers = ["Basic", "Pro", "Enterprise"]
        data = []
        for i in range(1, records + 1):
            tickets = random.randint(0, 15)
            nps = random.randint(1, 10)
            inactivity_days = random.randint(0, 45)
            churn = 1 if tickets > 8 or nps < 5 or inactivity_days > 30 else 0

            data.append(
                {
                    "customer_id": f"CUST-{2000 + i}",
                    "subscription_tier": random.choice(tiers),
                    "support_tickets_opened": tickets,
                    "nps_score": nps,
                    "days_since_last_login": inactivity_days,
                    "churn_flag": churn,
                }
            )
        return data

    @staticmethod
    def generate_sales_forecasting_dataset(records: int = 100) -> list[dict[str, Any]]:
        regions = ["North America", "EMEA", "APAC", "LATAM"]
        data = []
        for i in range(1, records + 1):
            hist_sales = round(random.uniform(50000, 500000), 2)
            growth = round(random.uniform(-0.05, 0.25), 4)
            pipeline_deals = random.randint(5, 50)
            target_sales = round(
                hist_sales * (1.0 + growth) + (pipeline_deals * 3500), 2
            )

            data.append(
                {
                    "region": random.choice(regions),
                    "historical_sales": hist_sales,
                    "growth_rate": growth,
                    "deals_in_pipeline": pipeline_deals,
                    "target_quarterly_sales": target_sales,
                }
            )
        return data

    @staticmethod
    def generate_inventory_optimization_dataset(
        records: int = 100,
    ) -> list[dict[str, Any]]:
        data = []
        for i in range(1, records + 1):
            stock = random.randint(50, 1000)
            reorder = random.randint(200, 500)
            holding_cost = round(random.uniform(1.0, 10.0), 2)
            lead_days = random.randint(3, 21)

            data.append(
                {
                    "sku_id": f"SKU-{3000 + i}",
                    "current_stock": stock,
                    "reorder_point": reorder,
                    "holding_cost": holding_cost,
                    "lead_time_days": lead_days,
                    "reorder_needed": stock <= reorder,
                }
            )
        return data

    @staticmethod
    def export_all_datasets_to_root(target_dir: str = "datasets") -> dict[str, str]:
        os.makedirs(target_dir, exist_ok=True)
        files_created = {}

        datasets_map = {
            "hr_attrition_dataset.json": MLDatasetGenerator.generate_hr_attrition_dataset(),
            "crm_churn_dataset.json": MLDatasetGenerator.generate_crm_churn_dataset(),
            "sales_forecasting_dataset.json": MLDatasetGenerator.generate_sales_forecasting_dataset(),
            "inventory_optimization_dataset.json": MLDatasetGenerator.generate_inventory_optimization_dataset(),
        }

        for filename, data in datasets_map.items():
            path = os.path.join(target_dir, filename)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            files_created[filename] = path

        return files_created
