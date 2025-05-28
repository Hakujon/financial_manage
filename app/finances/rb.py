class RBExpense:
    def __init__(self,
                 id: int | None = None,
                 category: str | None = None,
                 family_id: str | None = None):
        self.id = id
        self.category = category
        self.family_id = family_id

    def to_dict(self):
        data = {"id": self.id,
                "category": self.category,
                "family_id": self.family_id}
        filtered_data = {k: v for k, v in data.items() if v is not None}

        return filtered_data
