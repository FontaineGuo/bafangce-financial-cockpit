"""
数据库迁移脚本：删除portfolio_assets表中的allocation_amount列
执行时间: 2026-03-10
原因: allocation_amount字段在系统中没有被使用，但一直占用数据库存储空间
"""
import sqlite3
import os


def get_db_path():
    """获取数据库文件路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "db", "bafangce.db")


def check_column_exists(cursor, table_name, column_name):
    """检查表中是否存在指定列"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names


def get_table_structure(cursor, table_name):
    """获取表结构信息"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n当前表结构 ({table_name}):")
    print(f"{'序号':<6} | {'列名':<20} | {'类型':<15} | {'非空':<8} | {'主键':<8}")
    print("-" * 70)
    for i, col in enumerate(columns, 1):
        cid, name, type_, notnull, dflt_value, pk = col
        print(f"{i:<6} | {name:<20} | {type_:<15} | {'NO' if notnull else 'YES':<8} | {'YES' if pk else 'NO':<8}")
    print("-" * 70)


def drop_allocation_amount_column():
    """删除allocation_amount列"""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"[ERROR] 数据库文件不存在: {db_path}")
        return False

    print(f"[INFO] 数据库路径: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 显示迁移前表结构
        print("\n" + "=" * 70)
        print("迁移前表结构:")
        print("=" * 70)
        get_table_structure(cursor, "portfolio_assets")

        # 检查列是否存在
        if not check_column_exists(cursor, "portfolio_assets", "allocation_amount"):
            print("\n[INFO] allocation_amount列不存在，无需删除")
            return False

        print("\n[INFO] 找到allocation_amount列，准备删除...")

        # 删除列
        cursor.execute("ALTER TABLE portfolio_assets DROP COLUMN allocation_amount")
        conn.commit()

        print("[SUCCESS] 列删除成功")

        # 验证删除结果
        if check_column_exists(cursor, "portfolio_assets", "allocation_amount"):
            print("\n[WARNING] 删除后列仍然存在！")
            return False
        else:
            print("[SUCCESS] 验证通过: allocation_amount列已成功删除")

        # 显示迁移后表结构
        print("\n" + "=" * 70)
        print("迁移后表结构:")
        print("=" * 70)
        get_table_structure(cursor, "portfolio_assets")

        # 统计表中的数据行数
        cursor.execute("SELECT COUNT(*) FROM portfolio_assets")
        count = cursor.fetchone()[0]
        print(f"\n[STATS] portfolio_assets表中现有数据行数: {count}")

        return True

    except sqlite3.Error as e:
        print(f"\n[ERROR] 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] 未知错误: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("数据库迁移工具: 删除allocation_amount列")
    print("=" * 70)
    print(f"执行时间: 2026-03-10")
    print(f"目标: 从portfolio_assets表删除allocation_amount列")
    print("=" * 70)

    result = drop_allocation_amount_column()

    if result:
        print("\n" + "=" * 70)
        print("[SUCCESS] 迁移完成！")
        print("=" * 70)
        print("\n提示:")
        print("   1. 重启后端服务以使更改生效")
        print("   2. 确认前端代码已更新（allocation_amount相关代码已删除）")
        print("   3. 如有问题，可以重新创建数据库文件")
    else:
        print("\n" + "=" * 70)
        print("[ERROR] 迁移失败或未执行")
        print("=" * 70)


if __name__ == "__main__":
    main()