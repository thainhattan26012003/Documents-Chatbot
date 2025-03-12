import json
from neo4j import GraphDatabase

# Đọc dữ liệu JSON (đảm bảo file mã hóa UTF-8)
with open('bo_luat_processed.json', encoding='utf-8') as f:
    data = json.load(f)

# Kết nối đến Neo4j (điều chỉnh URI, username, password cho phù hợp)
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "nVPeG0FI4ESSpdyjDxL2Ir3qACimxJiACrlKOmKlBzs"))

def create_node(tx, label, properties):
    query = f"CREATE (n:{label} $props) RETURN id(n) as id"
    result = tx.run(query, props=properties)
    return result.single()["id"]

def create_relationship(tx, from_id, to_id, rel_type):
    query = (
        "MATCH (a), (b) "
        "WHERE id(a)=$from_id AND id(b)=$to_id "
        "CREATE (a)-[r:" + rel_type + "]->(b) "
        "RETURN r"
    )
    tx.run(query, from_id=from_id, to_id=to_id)

def process_section(tx, parent_id, section_key, section_data, label):
    """
    Tạo một node với label (ví dụ: Chapter, Article, Section) cùng với các thuộc tính:
    - name: tên (ví dụ: "Chương I", "Điều 1", "Mục 1")
    - title: tiêu đề nếu có
    - content: nội dung (nếu là chuỗi)
    Sau đó tạo quan hệ CONTAINS từ node cha (nếu parent_id không None) đến node vừa tạo.
    Sau đó đệ quy xử lý các phần con nếu có.
    """
    properties = {"name": section_key}
    if "title" in section_data:
        properties["title"] = section_data["title"]
    if "content" in section_data and isinstance(section_data["content"], str):
        properties["content"] = section_data["content"]
    
    node_id = create_node(tx, label, properties)
    if parent_id is not None:
        create_relationship(tx, parent_id, node_id, "CONTAINS")
    
    # Nếu "content" là một dict thì xử lý các phần con (ví dụ: các Điều trong Chương)
    if "content" in section_data and isinstance(section_data["content"], dict):
        for child_key, child_data in section_data["content"].items():
            # Phân loại label theo tiền tố: Nếu bắt đầu bằng "Điều" thì dùng Article, nếu bắt đầu bằng "Mục" thì dùng Section
            if child_key.startswith("Điều"):
                child_label = "Article"
            elif child_key.startswith("Mục"):
                child_label = "Section"
            else:
                child_label = "Node"
            process_section(tx, node_id, child_key, child_data, child_label)
    
    # Nếu có key "dieu" (trong một số mục như Mục có chứa các Điều)
    if "dieu" in section_data and isinstance(section_data["dieu"], dict):
        for child_key, child_data in section_data["dieu"].items():
            process_section(tx, node_id, child_key, child_data, "Article")

with driver.session() as session:
    # Tạo node gốc cho toàn bộ bộ luật
    law_id = session.write_transaction(create_node, "Law", {"name": "Bộ Luật Dân Sự Việt Nam"})
    
    # Duyệt qua các "Chương" ở cấp đầu tiên của file JSON
    for chapter_key, chapter_data in data.items():
        session.write_transaction(process_section, law_id, chapter_key, chapter_data, "Chapter")

driver.close()
