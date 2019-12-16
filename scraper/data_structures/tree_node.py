class TreeNode:
    def __init__(self, uid, name, parent_uid):
        self.uid = uid
        self.name = name
        self.parent_uid = parent_uid
        self.children = []
