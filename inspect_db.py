from app import create_app, db
from app.models.vehicle import Vehicle
from app.models.article import Article
from app.models.article_category import ArticleCategory

app = create_app()

with app.app_context():
    inspector = db.inspect(db.engine)
    
    # 检查所有表
    tables = inspector.get_table_names()
    print(f"数据库中的表: {tables}")
    print("=" * 60)
    
    # 检查文章表
    if 'articles' in tables:
        print("Articles表结构:")
        print("-" * 50)
        columns = inspector.get_columns('articles')
        for column in columns:
            print(f"列名: {column['name']}, 类型: {column['type']}, 是否可为空: {column['nullable']}")
        print()
    else:
        print("Articles表不存在!")
    
    # 检查文章分类表
    if 'article_categories' in tables:
        print("Article_categories表结构:")
        print("-" * 50)
        columns = inspector.get_columns('article_categories')
        for column in columns:
            print(f"列名: {column['name']}, 类型: {column['type']}, 是否可为空: {column['nullable']}")
        print()
    else:
        print("Article_categories表不存在!")
    
    # 检查vehicles表
    if 'vehicles' in tables:
        print("Vehicles表结构:")
        print("-" * 50)
        columns = inspector.get_columns('vehicles')
        for column in columns:
            print(f"列名: {column['name']}, 类型: {column['type']}, 是否可为空: {column['nullable']}")
    else:
        print("Vehicles表不存在!")