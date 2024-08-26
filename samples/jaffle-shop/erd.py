from dbterd.api import DbtErd

erd = DbtErd(algo="semantic", artifacts_dir="./samples/jaffle-shop").get_erd()
print("erd (dbml):", erd)
erd = DbtErd(target="mermaid", artifacts_dir="./samples/jaffle-shop").get_erd()
print("erd (mermaid):", erd)

print("===============")
print("===============")
erd = DbtErd(
    algo="semantic", target="mermaid", artifacts_dir="./samples/jaffle-shop"
).get_model_erd(node_unique_id="model.jaffle_shop.orders")
print("erd of orders (mermaid):", erd)
