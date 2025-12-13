# 持仓数据模型

class Holding:
    def __init__(self, id=None, product_code=None, product_name=None, product_type=None, quantity=None, purchase_price=None, current_price=None):
        self.id = id
        self.product_code = product_code  # 代码
        self.product_name = product_name  # 名称
        self.product_type = product_type  # 类型：stock, fund, etc.
        self.quantity = quantity  # 持有份额
        self.purchase_price = purchase_price  # 成本单价
        self.current_price = current_price  # 现价单价
    
    @property
    def cost_total(self):
        """成本总价"""
        if self.quantity and self.purchase_price:
            return self.quantity * self.purchase_price
        return 0
    
    @property
    def current_total(self):
        """现价总价"""
        if self.quantity and self.current_price:
            return self.quantity * self.current_price
        return 0
    
    @property
    def profit_total(self):
        """总盈利"""
        return self.current_total - self.cost_total
    
    @property
    def profit_rate(self):
        """盈利率"""
        if self.cost_total and self.cost_total > 0:
            return self.profit_total / self.cost_total
        return 0
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'current_price': self.current_price,
            'cost_total': self.cost_total,
            'current_total': self.current_total,
            'profit_total': self.profit_total
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        return cls(
            id=data.get('id'),
            product_code=data.get('product_code'),
            product_name=data.get('product_name'),
            product_type=data.get('product_type'),
            quantity=data.get('quantity'),
            purchase_price=data.get('purchase_price'),
            current_price=data.get('current_price')
        )
