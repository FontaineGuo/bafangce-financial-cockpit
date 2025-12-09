# 金融产品模型

class Product:
    def __init__(self, code, name, type, current_price=None, price_date=None):
        self.code = code
        self.name = name
        self.type = type  # stock, fund, etc.
        self.current_price = current_price
        self.price_date = price_date
    
    def to_dict(self):
        """转换为字典"""
        return {
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'current_price': self.current_price,
            'price_date': self.price_date
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        return cls(
            code=data.get('code'),
            name=data.get('name'),
            type=data.get('type'),
            current_price=data.get('current_price'),
            price_date=data.get('price_date')
        )
