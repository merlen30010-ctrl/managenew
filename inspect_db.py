from app import create_app, db
from app.models.vehicle import Vehicle

app = create_app()

with app.app_context():
    # 打印vehicles表的结构
    print("Vehicles表结构:")
    print("-" * 50)
    inspector = db.inspect(db.engine)
    columns = inspector.get_columns('vehicles')
    for column in columns:
        print(f"列名: {column['name']}, 类型: {column['type']}, 是否可为空: {column['nullable']}")