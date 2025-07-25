from tests import *


class TestMCActions(unittest.TestCase):

    def setUp(self):
        """Setup method to create MCPlayer and MCActionBase instances for each test."""
        self.mcp = MCPlayer(TEST_PLAYER_NAME, MC_SERVER_HOST, MC_RCON_PORT, FJ_PLUGIN_PORT)
        self.mca = MCActions(self.mcp)
        # You can add more common mappings to self.mca.block_id_map here if needed for extensive testing,
        # or ensure _initialize_block_id_maps is comprehensive enough.

    def test_base_init(self):
        self.assertIsNotNone(self.mca)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
