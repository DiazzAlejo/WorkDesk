import tkinter as tk
import unittest

from app.ui.shared.components import SectionFrame


class SharedComponentTests(unittest.TestCase):
    def test_section_frame_defaults_and_variants(self):
        root = tk.Tk()
        root.withdraw()
        try:
            default = SectionFrame(root, "Default")
            compact = SectionFrame(root, "Compact", size="compact", variant="muted")
            accent = SectionFrame(root, "Accent", variant="accent", show_title=False)
            self.assertEqual(default.props.size, "comfortable")
            self.assertEqual(compact.props.variant, "muted")
            self.assertFalse(accent.props.show_title)
            default.destroy()
            compact.destroy()
            accent.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
