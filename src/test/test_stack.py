import unittest

from src.ds_algo.stack import UndoStack


class UndoStackTest(unittest.TestCase):
    def test_stack_pops_latest_state_first(self):
        stack = UndoStack()

        stack.push({"turn": 1})
        stack.push({"turn": 2})

        self.assertEqual(stack.pop(), {"turn": 2})
        self.assertEqual(stack.pop(), {"turn": 1})
        self.assertIsNone(stack.pop())

    def test_stack_discards_oldest_state_when_full(self):
        stack = UndoStack(max_size=2)

        stack.push("old")
        stack.push("middle")
        stack.push("new")

        self.assertEqual(stack.pop(), "new")
        self.assertEqual(stack.pop(), "middle")
        self.assertIsNone(stack.pop())

    def test_clear_removes_all_states(self):
        stack = UndoStack()

        stack.push("state")
        stack.clear()

        self.assertTrue(stack.is_empty())


if __name__ == "__main__":
    unittest.main()
