from enum import Enum


class RedBlackTree:
    class Color(Enum):
        RED = 1
        BLACK = 2

    class RedBlackNode:
        key = None
        data = None
        left = None
        right = None
        color = None

        def __init__(self, key, data, left, right, color):
            self.key = key
            self.data = data
            self.left = left
            self.right = right
            self.color = color

    # header is a dummy node to eliminate special cases involving the root
    header = None
    # nullNode indicates the obvious thing
    nullNode = None
    # we must keep track of the current, parent, grandparent, and great grandparent (for reattachment)
    current = None
    parent = None
    grand = None
    great = None

    def __init__(self):
        self.nullNode = self.RedBlackNode(
            None, None, None, None, self.Color.BLACK)
        self.nullNode.left = self.nullNode.right = self.nullNode

        # "" is less than any other string, so the header has key ""
        self.header = self.RedBlackNode(
            "", None, self.nullNode, self.nullNode, self.Color.BLACK)

    def find(self, key):
        def findRec(node):
            if (node == self.nullNode):
                return None
            elif (key == node.key):
                return node.data
            elif (key < node.key):
                return findRec(node.left)
            else:
                return findRec(node.right)

        if (self.header.right == self.nullNode):
            return None
        else:
            return findRec(self.header.right)

    def getPreorder(self):
        def getPreorderRec(node):
            preorder = ""
            if (node != self.nullNode):
                preorder += node.key + " "
                preorder += getPreorderRec(node.left)
                preorder += getPreorderRec(node.right)

            return preorder

        if (self.header.right == self.nullNode):
            return ""
        else:
            return getPreorderRec(self.header.right)

    def getInorder(self):
        def getInorderRec(node):
            inorder = ""
            if (node != self.nullNode):
                inorder += getInorderRec(node.left)
                inorder += node.key + " "
                inorder += getInorderRec(node.right)

            return inorder

        if (self.header.right == self.nullNode):
            return ""
        else:
            return getInorderRec(self.header.right)

    def getPostorder(self):
        def getPostorderRec(node):
            postorder = ""
            if (node != self.nullNode):
                postorder += getPostorderRec(node.left)
                postorder += getPostorderRec(node.right)
                postorder += node.key + " "

            return postorder

        if (self.header.right == self.nullNode):
            return ""
        else:
            return getPostorderRec(self.header.right)

# performs a single right rotation at node and returns the new root of the subtree
    def rotateRight(self, node):
        child = node.left
        node.left = child.right
        child.right = node
        return child

# symmetric case
    def rotateLeft(self, node):
        child = node.right
        node.right = child.left
        child.left = node
        return child

# performs the correct rotation given the data to be inserted and the parent of the node we want to rotate at
    def rotate(self, key, theParent):
        if (key < theParent.key):
            theParent.left = self.rotateRight(
                theParent.left) if key < theParent.left.key else self.rotateLeft(theParent.left)
            return theParent.left
        else:
            theParent.right = self.rotateRight(
                theParent.right) if key < theParent.right.key else self.rotateLeft(theParent.right)
            return theParent.right

# flips colors and rotates if needed
    def reorient(self, key):
        # flip colors
        self.current.color = self.Color.RED
        self.current.left.color = self.Color.BLACK
        self.current.right.color = self.Color.BLACK

        # perform rotations
        if self.parent.color == self.Color.RED:
            self.grand.color = self.Color.RED
            if ((key < self.grand.key) != (key < self.parent.key)):  # LR and RL cases
                # rotate at the parent of the current node
                self.parent = self.rotate(key, self.grand)
            # rotate at the grandparent of the current node
            self.current = self.rotate(key, self.great)
            self.current.color = self.Color.BLACK

        self.header.right.color = self.Color.BLACK  # make root black

# inserts data into the tree
    def insert(self, key, data):
        self.current = self.parent = self.grand = self.header
        self.nullNode.key = key

        while (self.current.key != key):
            self.great = self.grand
            self.grand = self.parent
            self.parent = self.current
            self.current = self.current.left if key < self.current.key else self.current.right

            if (self.current.left.color == self.Color.RED and self.current.right.color == self.Color.RED):
                self.reorient(key)

        # insertion fails (duplicate key)
        if (self.current != self.nullNode):
            return
        self.current = self.RedBlackNode(
            key, data, self.nullNode, self.nullNode, self.Color.BLACK)

        # attach to parent
        if (key < self.parent.key):
            self.parent.left = self.current
        else:
            self.parent.right = self.current
        self.reorient(key)
