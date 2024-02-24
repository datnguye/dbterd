from dbterd.api import DbtErd

erd = DbtErd().get_erd()
print("erd (dbml):", erd)
erd = DbtErd(target="mermaid").get_erd()
print("erd (mermaid):", erd)

print("===============")
print("===============")
fact_number_erd = DbtErd(target="mermaid").get_model_erd(
    node_unique_id="model.dbt_resto.fact_number"
)
print("erd of fact_number (mermaid):", fact_number_erd)

print("===============")
print("===============")
dim_prize_erd = DbtErd(target="mermaid").get_model_erd(
    node_unique_id="model.dbt_resto.dim_prize"
)
print("erd of dim_date (mermaid):", dim_prize_erd)
